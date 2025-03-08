from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Review, ReviewVote, User, Ride, ReviewResponse  
from schemas import ReviewCreate, ReviewDisplay, ReviewVoteCreate, ReviewResponseCreate
from utils.notifications import moderate_text  # ✅ AI-based text moderation
from utils.notifications import send_system_notifications
from typing import List, Optional
from utils.notifications import send_email
from utils.sentiment_analysis import moderate_text






router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

# 📌 Yorum oluşturma (Sadece ilgili yolculuğa katılan kullanıcılar yorum yapabilir)
@router.post("/", response_model=ReviewDisplay)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """
    Allows passengers to leave reviews about the ride, driver, or service.
    """

    # ✅ Yolculuk ve kullanıcı kontrolü
    ride = db.query(Ride).filter(Ride.id == review.ride_id).first()
    reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
    reviewee = db.query(User).filter(User.id == review.reviewee_id).first()

    if not ride or not reviewer or not reviewee:
        raise HTTPException(status_code=404, detail="Ride, reviewer, or reviewee not found.")

    # ✅ Kullanıcılar sadece yolculuğa katıldıkları kişilere yorum yapabilir
    booking_exists = db.query(Ride).filter(
        Ride.id == review.ride_id, 
        Ride.driver_id == review.reviewee_id
    ).first()

    if not booking_exists:
        raise HTTPException(status_code=403, detail="You can only review people from your ride.")

    # ✅ Spam veya kötüye kullanım içeren yorumları engelle
    if moderate_text(review.review_text):
        raise HTTPException(status_code=400, detail="Your review contains inappropriate content.")

    # ✅ Yeni yorumu veritabanına ekle
    new_review = Review(
        ride_id=review.ride_id,
        reviewer_id=review.reviewer_id,
        reviewee_id=review.reviewee_id,
        review_category=review.review_category,
        star_rating=review.star_rating,
        review_text=review.review_text,
        anonymous_review=review.anonymous_review
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # ✅ Ortalama puanı güncelle
    reviews = db.query(Review).filter(Review.reviewee_id == review.reviewee_id).all()
    total_score = sum(r.star_rating for r in reviews)
    average_rating = total_score / len(reviews)
    reviewee.rating = round(average_rating, 2)  # Kullanıcının ortalama puanını güncelle

    db.commit()

    return new_review

# 📌 Yorumları listeleme (Filtrelenebilir)
@router.get("/", response_model=List[ReviewDisplay])
def get_reviews(
    ride_id: Optional[int] = None,
    reviewee_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves reviews based on optional filters (ride, reviewer, or reviewee).
    """
    query = db.query(Review)

    if ride_id:
        query = query.filter(Review.ride_id == ride_id)
    if reviewee_id:
        query = query.filter(Review.reviewee_id == reviewee_id)
    if reviewer_id:
        query = query.filter(Review.reviewer_id == reviewer_id)

    reviews = query.all()

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found.")

    return reviews

# 📌 Yorum güncelleme (Sadece yorumu yazan kişi değiştirebilir)
@router.put("/{review_id}", response_model=ReviewDisplay)
def update_review(review_id: int, updated_review: ReviewCreate, db: Session = Depends(get_db)):
    """
    Allows the author to update their review.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # ✅ Yalnızca yorumu yazan kişi değiştirebilir
    if updated_review.reviewer_id != review.reviewer_id:
        raise HTTPException(status_code=403, detail="You can only edit your own review.")

    review.star_rating = updated_review.star_rating
    review.review_text = updated_review.review_text
    review.anonymous_review = updated_review.anonymous_review

    db.commit()
    db.refresh(review)

    return review

# 📌 Yorum silme (Sadece yazan kişi veya admin silebilir)
@router.delete("/{review_id}")
def delete_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Allows users to delete their own reviews or admin to remove any review.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # ✅ Yalnızca yorumu yazan kişi veya admin silebilir
    user = db.query(User).filter(User.id == user_id).first()

    if not user or (user.id != review.reviewer_id and user.role != "admin"):
        raise HTTPException(status_code=403, detail="You don't have permission to delete this review.")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted successfully."}

# 📌 Beğeni/Beğenmeme ekleme (Like/Dislike)
@router.post("/{review_id}/vote")
def vote_review(vote: ReviewVoteCreate, db: Session = Depends(get_db)):
    """
    Allows users to like or dislike a review.
    """
    review = db.query(Review).filter(Review.id == vote.review_id).first()
    user = db.query(User).filter(User.id == vote.voter_id).first()

    if not review or not user:
        raise HTTPException(status_code=404, detail="Review or user not found.")

    # ✅ Kullanıcı zaten oy vermiş mi kontrol et
    existing_vote = db.query(ReviewVote).filter(
        ReviewVote.review_id == vote.review_id,
        ReviewVote.voter_id == vote.voter_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted on this review.")

    # ✅ Yeni oy ekle
    new_vote = ReviewVote(
        review_id=vote.review_id,
        voter_id=vote.voter_id,
        vote_type=vote.vote_type
    )

    db.add(new_vote)
    
    # ✅ Beğeni/Beğenmeme sayısını güncelle
    if vote.vote_type == "like":
        review.likes += 1
    elif vote.vote_type == "dislike":
        review.dislikes += 1

    db.commit()

    return {"message": "Vote recorded successfully."}

# 📌 Yorumlara yanıt verme
@router.post("/{review_id}/response")
def respond_to_review(response: ReviewResponseCreate, db: Session = Depends(get_db)):
    """
    Allows users to reply to a review.
    """
    review = db.query(Review).filter(Review.id == response.review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    new_response = ReviewResponse(
        review_id=response.review_id,
        responder_id=response.responder_id,
        response_text=response.response_text
    )

    db.add(new_response)
    db.commit()

    return {"message": "Response added successfully."}
