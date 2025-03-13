from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Review, ReviewVote, User, Ride, ReviewResponse  
from schemas import ReviewCreate, ReviewDisplay, ReviewVoteCreate, ReviewResponseCreate
from utils.sentiment_analysis import ai_moderation  # ✅ AI-Based Moderation
from utils.dependencies import get_current_user  # ✅ User Authentication
from typing import List, Optional
from transformers import pipeline

# ✅ Load the AI sentiment model
model_path = "./models/nlptown_bert"
sentiment_analysis_model = pipeline(
    "sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", cache_dir=model_path
)

# ✅ Initialize router
router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

# def update_user_review_stats(db: Session, user_id: int):
#     """
#     ✅ Updates the average rating, total likes, and total dislikes of a user.
#     """
#     reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()
    
#     if not reviews:
#         new_average = 0.0
#         total_likes, total_dislikes = 0, 0
#     else:
#         new_average = round(sum(r.star_rating for r in reviews) / len(reviews), 2)
#         total_likes = sum(r.likes for r in reviews)
#         total_dislikes = sum(r.dislikes for r in reviews)

#     # ✅ Update user rating, likes, and dislikes
#     user = db.query(User).filter(User.id == user_id).first()
#     if user:
#         user.average_rating = new_average
#         user.total_likes = total_likes
#         user.total_dislikes = total_dislikes
#         db.commit()

def update_user_review_stats(db: Session, user_id: int):
    """
    ✅ Ensures the reviewee's rating, total likes, and total dislikes are correctly calculated.
    """
    reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()

    if not reviews:
        new_average = 0.0
        total_likes, total_dislikes = 0, 0
    else:
        new_average = round(sum(r.star_rating for r in reviews) / len(reviews), 2)

        # ✅ Recalculate total likes and dislikes based on ReviewVote table
        total_likes = db.query(ReviewVote).filter(ReviewVote.vote_type == "like").count()
        total_dislikes = db.query(ReviewVote).filter(ReviewVote.vote_type == "dislike").count()

    # ✅ Update the user record with the latest data
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.average_rating = new_average
        user.total_likes = total_likes
        user.total_dislikes = total_dislikes
        db.commit()


# 📌 Create a Review
@router.post("/", response_model=ReviewDisplay)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """
    ✅ Creates a new review, updates the reviewee's rating, and applies AI moderation.
    """
    ride = db.query(Ride).filter(Ride.id == review.ride_id).first()
    reviewer = db.query(User).filter(User.id == review.reviewer_id).first()
    reviewee = db.query(User).filter(User.id == review.reviewee_id).first()

    if not ride or not reviewer or not reviewee:
        raise HTTPException(status_code=404, detail="Ride, reviewer, or reviewee not found.")

    existing_review = db.query(Review).filter(
        Review.ride_id == review.ride_id,
        Review.reviewer_id == review.reviewer_id,
        Review.reviewee_id == review.reviewee_id
    ).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="❌ You have already reviewed this user for this ride.")

    # ✅ AI moderation check
    if ai_moderation(review.review_text):
        raise HTTPException(status_code=400, detail="🚫 Your review contains prohibited content.")

    review_data = review.dict()
    review_data.pop("media_url", None)  # ✅ Ensure 'media_url' is not passed if not in the model

    new_review = Review(**review_data)
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    update_user_review_stats(db, review.reviewee_id)
    return new_review

# 📌 Add Like/Dislike with Toggle & Change Support
# @router.post("/{review_id}/vote")
# def vote_review(vote: ReviewVoteCreate, db: Session = Depends(get_db)):
#     """
#     ✅ Allows users to like/dislike a review with toggle & change support.
#     """
#     review = db.query(Review).filter(Review.id == vote.review_id).first()
#     if not review:
#         raise HTTPException(status_code=404, detail="Review not found.")

#     existing_vote = db.query(ReviewVote).filter(
#         ReviewVote.review_id == vote.review_id,
#         ReviewVote.voter_id == vote.voter_id
#     ).first()

#     # ✅ Toggle or Change Vote Logic
#     if existing_vote:
#         if existing_vote.vote_type == vote.vote_type:
#             db.delete(existing_vote)
#             review.likes -= 1 if vote.vote_type == "like" else 0
#             review.dislikes -= 1 if vote.vote_type == "dislike" else 0
#             db.commit()
#             update_user_review_stats(db, review.reviewee_id)
#             return {"message": "Your vote has been removed."}
#         else:
#             review.likes += 1 if vote.vote_type == "like" else -1
#             review.dislikes += 1 if vote.vote_type == "dislike" else -1
#             existing_vote.vote_type = vote.vote_type
#             db.commit()
#             update_user_review_stats(db, review.reviewee_id)
#             return {"message": "Your vote has been updated."}

#     # ✅ If no vote exists, add a new vote
#     db.add(ReviewVote(**vote.dict()))
#     review.likes += 1 if vote.vote_type == "like" else 0
#     review.dislikes += 1 if vote.vote_type == "dislike" else 0
#     db.commit()
#     update_user_review_stats(db, review.reviewee_id)
    
#     return {"message": "Vote recorded successfully."}


@router.post("/{review_id}/vote")
def vote_review(review_id: int, vote: ReviewVoteCreate, db: Session = Depends(get_db)):
    """
    ✅ Allows users to like/dislike a review while keeping the review table updated with the correct counts.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    existing_vote = db.query(ReviewVote).filter(
        ReviewVote.review_id == review_id,
        ReviewVote.voter_id == vote.voter_id
    ).first()

    # ✅ Toggle or Update Existing Vote Logic
    if existing_vote:
        if existing_vote.vote_type == vote.vote_type:
            # ✅ Remove vote if the user clicks again (unlike/dislike)
            db.delete(existing_vote)
            if vote.vote_type == "like":
                review.likes = max(0, review.likes - 1)
            elif vote.vote_type == "dislike":
                review.dislikes = max(0, review.dislikes - 1)
            db.commit()
            update_user_review_stats(db, review.reviewee_id)
            return {"message": "Your vote has been removed."}
        else:
            # ✅ Change vote from like to dislike or vice versa
            if existing_vote.vote_type == "like":
                review.likes = max(0, review.likes - 1)
                review.dislikes += 1
            else:
                review.dislikes = max(0, review.dislikes - 1)
                review.likes += 1
            existing_vote.vote_type = vote.vote_type
            db.commit()
            update_user_review_stats(db, review.reviewee_id)
            return {"message": "Your vote has been updated."}

    # ✅ If no existing vote, add a new vote and update counts
    new_vote = ReviewVote(**vote.dict())
    db.add(new_vote)
    if vote.vote_type == "like":
        review.likes += 1
    elif vote.vote_type == "dislike":
        review.dislikes += 1

    db.commit()
    update_user_review_stats(db, review.reviewee_id)

    return {"message": "Vote recorded successfully."}


# 📌 Retrieve Reviews (With Filters)
@router.get("/", response_model=List[ReviewDisplay])
def get_reviews(
    ride_id: Optional[int] = None,
    reviewee_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    ✅ Retrieves reviews based on optional filters (ride, reviewer, or reviewee).
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

# 📌 Update a Review
@router.put("/{review_id}", response_model=ReviewDisplay)
def update_review(review_id: int, updated_review: ReviewCreate, db: Session = Depends(get_db)):
    """
    ✅ Allows users to update their own reviews.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    if updated_review.reviewer_id != review.reviewer_id:
        raise HTTPException(status_code=403, detail="You can only edit your own review.")

    if ai_moderation(updated_review.review_text):
        raise HTTPException(status_code=400, detail="Your updated review contains prohibited content.")

    for key, value in updated_review.dict().items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    update_user_review_stats(db, review.reviewee_id)
    
    return review

# 📌 Delete a Review
@router.delete("/{review_id}")
def delete_review(review_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    ✅ Allows users to delete their own reviews or admin to remove any review.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    user = db.query(User).filter(User.id == user_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    if not user or (user.id != review.reviewer_id and user.role != "admin"):
        raise HTTPException(status_code=403, detail="You don't have permission to delete this review.")

    db.delete(review)
    db.commit()
    update_user_review_stats(db, review.reviewee_id)

    return {"message": "Review deleted successfully."}

# 📌 Respond to a Review
@router.post("/respond")
def respond_to_review(response: ReviewResponseCreate, db: Session = Depends(get_db)):
    """
    ✅ Allows users to respond to reviews while filtering banned words.
    """
    if ai_moderation(response.response_text):
        raise HTTPException(status_code=400, detail="Response contains banned content.")

    new_response = ReviewResponse(**response.dict())
    db.add(new_response)
    db.commit()
    
    return {"message": "Response added"}
