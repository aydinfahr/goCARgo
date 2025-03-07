from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session, joinedload  # ✅ Efficiently load related data
from db import db_review
from schemas import ReviewDisplay, ReviewBase, ReviewDeleteResponse, ReviewVoteBase, ReviewVoteDisplay, ReviewVoteCount
from typing import List, Optional
from db.models import DbReview, DbReviewVote, DbReviewResponse, DbUser
from db.database import get_db
from enum import Enum  # ✅ Import Enum for dropdown options
from sqlalchemy import func  # ✅ Import func for SQL functions
from textblob import TextBlob
from db.utils import moderate_text



# ✅ List of banned words (you can expand this)
BANNED_WORDS = ["bad", "terrible", "awful", "stupid", "hate", "worst", "ugly", "idiot", "scam", "fake"]

def contains_banned_word(comment: str) -> bool:
    """
    Checks if the comment contains any banned words.
    """
    if not comment:
        return False
    lower_comment = comment.lower()  # ✅ Make it case insensitive
    for word in BANNED_WORDS:
        if word in lower_comment:
            return True
    return False

def analyze_sentiment(comment: str) -> float:
    """
    Analyze the sentiment of a comment using TextBlob.
    Returns a polarity score between -1 (very negative) and 1 (very positive).
    """
    sentiment_score = TextBlob(comment).sentiment.polarity
    print(f"Sentiment Score: {sentiment_score} for comment: {comment}")  # ✅ Log for debugging
    return sentiment_score



# ✅ Define allowed vote types (Dropdown selection)
class VoteType(str, Enum):
    like = "like"
    dislike = "dislike"


# ✅ Define allowed review types (Dropdown selection)
class ReviewType(str, Enum):
    driver = "driver"
    passenger = "passenger"
    car = "car"
    service = "service"


# ✅ Define FastAPI router for review-related endpoints
router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

# ======================================================================================
# 📌 CREATE A NEW REVIEW WITH AI SENTIMENT ANALYSIS AND AVERAGE RATING UPDATE
# ======================================================================================

# ✅ Sentiment Analysis Function
def analyze_sentiment(text: Optional[str]) -> float:
    """Analyzes the sentiment of a given text and returns a sentiment score."""
    if not text:
        return 0  # If no comment is provided, assume neutral sentiment
    sentiment = TextBlob(text).sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)
    return sentiment


@router.post("/", response_model=ReviewDisplay)
def create_review(
    ride_id: int = Form(...),
    reviewer_id: int = Form(...),
    reviewee_id: int = Form(...),
    review_type: ReviewType = Form(...),  # ✅ Uses dropdown selection
    rating: float = Form(...),
    comment: Optional[str] = Form(None),
    is_anonymous: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new review for a ride, driver, passenger, or service.
     - Prevents duplicate reviews for the same ride.
    - Uses AI Sentiment Analysis to block fake or abusive reviews.
    - Uses manual word filtering for extra protection.
    """

    #     # ✅ Check for banned words
    # if contains_banned_word(comment):
    #     raise HTTPException(status_code=400, detail="Your comment contains inappropriate language.")



    # # ✅ AI Sentiment Analysis: Block abusive or fake reviews
    # sentiment_score = analyze_sentiment(comment)
    
    # if sentiment_score < -0.5:
    #     raise HTTPException(status_code=400, detail="Review contains abusive or negative language.")
    

    # ✅ Moderation Check (DeepAI + Manual)
    if comment and moderate_text(comment):
        raise HTTPException(status_code=400, detail="Review contains offensive or inappropriate language.")



    # ✅ Check if the same review already exists
    existing_review = db.query(DbReview).filter(
        DbReview.ride_id == ride_id,
        DbReview.reviewer_id == reviewer_id,
        DbReview.reviewee_id == reviewee_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this ride/user.")


    # ✅ Ensure file is truly optional
    media_url = None
    if file and file.filename:
        media_url = f"/uploads/{file.filename}"

    # ✅ Create new review entry
    new_review = DbReview(
        ride_id=ride_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        review_type=review_type.value,
        rating=rating,
        comment=comment,
        is_anonymous=is_anonymous,
        media_url=media_url
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # ✅ Update the average rating of the reviewee
    average_rating = db.query(func.avg(DbReview.rating)).filter(DbReview.reviewee_id == reviewee_id).scalar()
    
    # ✅ Update the reviewee's profile with the new average rating
    reviewee = db.query(DbUser).filter(DbUser.id == reviewee_id).first()
    if reviewee:
        reviewee.average_rating = round(average_rating, 2) if average_rating else 0
        db.commit()

    return new_review




# ==============================================================
# 📌 CEAT RESPONSE A REVIEW
# ==============================================================
@router.post("/", response_model=ReviewDisplay)
def create_review(
    ride_id: int = Form(...),
    reviewer_id: int = Form(...),
    reviewee_id: int = Form(...),
    review_type: ReviewType = Form(...),
    rating: float = Form(...),
    comment: Optional[str] = Form(None),
    is_anonymous: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new review, but first checks for fake or abusive content.
    """

    # ✅ If the comment exists, check its sentiment
    if comment:
        sentiment_score = analyze_sentiment(comment)
        if sentiment_score < -0.5:  # Too negative?
            raise HTTPException(status_code=400, detail="Your review is too negative or inappropriate.")

    # ✅ Continue with normal review creation
    media_url = None
    if file and file.filename:
        media_url = f"/uploads/{file.filename}"

    new_review = DbReview(
        ride_id=ride_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        review_type=review_type.value,
        rating=rating,
        comment=comment,
        is_anonymous=is_anonymous,
        media_url=media_url
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


# ==============================================================
# 📌 LIKE OR DISLIKE A REVIEW
# ==============================================================

@router.post("/{review_id}/vote")
def vote_review(
    review_id: int,
    vote_type: VoteType = Query(..., description="Available values: like, dislike"),  # ✅ Forces dropdown selection
    user_id: int = Query(..., description="User ID of the voter"),  # ✅ Query param for user ID
    db: Session = Depends(get_db)
):
    """
    Allows users to vote on a review (like/dislike).
    
    - Prevents duplicate votes from the same user.
    - **vote_type** must be "like" or "dislike".
    - Ensures that the user exists before voting.
    - Returns updated like and dislike counts.
    """

    # ✅ Check if review exists
    review = db.query(DbReview).filter(DbReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # ✅ Check if the user exists
    user = db.query(DbUser).filter(DbUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid user ID. User does not exist.")


    # ✅ Check if user already voted on this review
    existing_vote = db.query(DbReviewVote).filter(
        DbReviewVote.review_id == review_id,
        DbReviewVote.user_id == user_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted on this review")

    # ✅ Create a new vote entry
    new_vote = DbReviewVote(
        review_id=review_id,
        user_id=user_id,
        vote_type=vote_type.value  # Store the string value
    )

    db.add(new_vote)


    # ✅ Update like & dislike count in reviews table
    if vote_type.value == "like":
        review.likes += 1
    elif vote_type.value == "dislike":
        review.dislikes += 1


    db.commit()
    db.refresh(new_vote)

    return {
        "message": f"Vote recorded successfully: {vote_type.value}",
        "likes": review.likes,
        "dislikes": review.dislikes
    }

# ==============================================================
# 📌 GET REVIEWS WITH OPTIONAL FILTERS
# ==============================================================

@router.get("/", response_model=List[ReviewDisplay])
def get_reviews(
    ride_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    reviewee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves reviews based on optional filters:
    - ride_id (Filter by ride)
    - reviewer_id (Filter by reviewer)
    - reviewee_id (Filter by reviewee)
    - Includes response messages, like/dislike count, and average rating.
    """

    try:

      # ✅ Ensure at least one filter is provided
      if ride_id is None and reviewer_id is None and reviewee_id is None:
        raise HTTPException(status_code=400, detail="At least one filter (ride_id, reviewer_id, reviewee_id) is required.")

      # ✅ Query reviews & load responses efficiently
      query = db.query(DbReview).options(joinedload(DbReview.responses))  # ✅ Load review responses

      if ride_id is not None:
        query = query.filter(DbReview.ride_id == ride_id)
      if reviewer_id is not None:
        query = query.filter(DbReview.reviewer_id == reviewer_id)
      if reviewee_id is not None:
        query = query.filter(DbReview.reviewee_id == reviewee_id)

      reviews = query.all()

      if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for the given criteria.")

      # ✅ Calculate like & dislike counts + average rating for each reviewee
      review_list = []
      for review in reviews:
        like_count = db.query(DbReviewVote).filter(
            DbReviewVote.review_id == review.id,
            DbReviewVote.vote_type == "like"
        ).count()
        
        dislike_count = db.query(DbReviewVote).filter(
            DbReviewVote.review_id == review.id,
            DbReviewVote.vote_type == "dislike"
        ).count()

        # ✅ Calculate average rating for the reviewee
        reviewee_ratings = db.query(DbReview.rating).filter(DbReview.reviewee_id == review.reviewee_id).all()
        if reviewee_ratings:
            avg_rating = sum(r[0] for r in reviewee_ratings) / len(reviewee_ratings)
        else:
            avg_rating = 0  # No reviews yet

        # Debugging Print Statements
        print(f"Review ID: {review.id}, Likes: {like_count}, Dislikes: {dislike_count}, Avg Rating: {avg_rating}")


        # ✅ Convert ORM object to dict and add calculated fields
        review_dict = review.__dict__
        review_dict["vote_count"] = {"likes": like_count, "dislikes": dislike_count}
        review_dict["responses"] = review.responses  # ✅ Include review responses
        review_dict["average_rating"] = round(avg_rating, 2) if avg_rating else 0  # ✅ Round to 2 decimal places

        review_list.append(review_dict)

      return review_list

    except Exception as e:
     print(f"Error: {str(e)}")  # ✅ Debugging print
     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



# ==============================================================
# 📌 GET A SPECIFIC REVIEW BY ID
# ==============================================================
@router.get("/{id}", response_model=ReviewDisplay)
def get_review(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific review by ID.
    """

    review = db.query(DbReview).filter(DbReview.id == id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    return review  # ✅ FastAPI automatically converts ORM object to Pydantic schema


# ==============================================================
# 📌 UPDATE A REVIEW
# ==============================================================
@router.put("/{id}", response_model=ReviewDisplay)
def update_review(
    id: int,
    request: ReviewBase = Depends(),  # ✅ Supports form data
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = None  # ✅ Supports file upload
):
    """
    Updates an existing review.
    """

    review = db.query(DbReview).filter(DbReview.id == id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found for this id.")
    
    # ✅ Handle file upload (update file URL if provided)
    media_url = review.media_url
    if file:
        media_url = f"/uploads/{file.filename}"

    # ✅ Update only the fields provided in the request
    review.ride_id = request.ride_id
    review.reviewer_id = request.reviewer_id
    review.reviewee_id = request.reviewee_id
    review.review_type = request.review_type
    review.rating = request.rating
    review.comment = request.comment
    review.is_anonymous = request.is_anonymous
    review.media_url = media_url

    db.commit()
    db.refresh(review)
    
    return review


# ==============================================================
# 📌 DELETE A REVIEW
# ==============================================================
@router.delete("/{id}", response_model=ReviewDeleteResponse)
def delete_review(id: int, db: Session = Depends(get_db)):
    """
    Deletes a review by ID.
    """

    deleted_review = db_review.delete_review(db, id)
    if not deleted_review:
        raise HTTPException(status_code=404, detail="Review not found or already deleted.")
    return ReviewDeleteResponse(message="Review successfully deleted.")


# ==============================================================
# 📌 RESPONSE A REVIEW
# ==============================================================

@router.post("/{review_id}/response")
def add_review_response(
    review_id: int,
    responder_id: int = Form(...),  # The user/admin who responds
    response_text: str = Form(...),  # The text of the response
    db: Session = Depends(get_db)
):
    """
    Allows users or admins to respond to a review.
    """

    # ✅ Check if the review exists
    review = db.query(DbReview).filter(DbReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # ✅ Create a new response
    response = DbReviewResponse(
        review_id=review_id,
        responder_id=responder_id,
        response_text=response_text
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return {"message": "Response added successfully"}
