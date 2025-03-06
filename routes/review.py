from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from db import db_review
from schemas import ReviewDisplay, ReviewBase, ReviewDeleteResponse, ReviewVoteBase
from typing import List, Optional
from db.models import DbReview, DbReviewVote
from db.database import get_db
from enum import Enum  # ✅ Enum kütüphanesini ekledik
from fastapi import Form  # ✅ Form verilerini alabilmek için ekleyelim


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# ✅ Define allowed vote types
class VoteType(str, Enum):
    like = "like"
    dislike = "dislike"


# 📌 Create a new review with file upload support
@router.post("/", response_model=ReviewDisplay)
def create_review(
    ride_id: int = Form(...),
    reviewer_id: int = Form(...),
    reviewee_id: int = Form(...),
    review_type: str = Form(...),
    rating: float = Form(...),
    comment: Optional[str] = Form(None),
    is_anonymous: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        print(f"Received request: {ride_id}, {reviewer_id}, {reviewee_id}, {review_type}, {rating}, {comment}, {is_anonymous}")  # Debugging print

        # 📌 Check if the same review already exists
        existing_review = db.query(DbReview).filter(
            DbReview.ride_id == ride_id,
            DbReview.reviewer_id == reviewer_id,
            DbReview.reviewee_id == reviewee_id
        ).first()

        if existing_review:
            raise HTTPException(status_code=400, detail="Review already exists for this ride and user.")

        # 📌 Handle file upload (save file path)
        media_url = None
        if file:
            media_url = f"/uploads/{file.filename}"  # Example: Store the file path

        # 📌 Create a new review instance
        new_review = DbReview(
            ride_id=ride_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            review_type=review_type,
            rating=rating,
            comment=comment,
            is_anonymous=is_anonymous,
            media_url=media_url  # Store media file URL
        )

        # 📌 Add to database
        db.add(new_review)
        db.commit()
        db.refresh(new_review)

        return new_review

    except HTTPException as http_error:
        raise http_error  # Re-raise HTTPException errors

    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")  # Debugging print
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# 📌 Like or Dislike a review

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
    """

    # Check if review exists
    review = db.query(DbReview).filter(DbReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Check if user already voted on this review
    existing_vote = db.query(DbReviewVote).filter(
        DbReviewVote.review_id == review_id,
        DbReviewVote.user_id == user_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted on this review")

    # Create a new vote entry
    new_vote = DbReviewVote(
        review_id=review_id,
        user_id=user_id,
        vote_type=vote_type.value  # ✅ Ensure we store the string value
    )

    db.add(new_vote)
    db.commit()
    db.refresh(new_vote)

    return {"message": f"Vote recorded successfully: {vote_type.value}"}




# 📌 Get reviews with optional filters (ride_id, reviewer_id, reviewee_id)
@router.get("/", response_model=List[ReviewDisplay])
def get_reviews(
    ride_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    reviewee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # 📌 Ensure at least one filter is provided
    if ride_id is None and reviewer_id is None and reviewee_id is None:
        raise HTTPException(status_code=400, detail="At least one filter (ride_id, reviewer_id, reviewee_id) is required.")

    query = db.query(DbReview)

    if ride_id is not None:
        query = query.filter(DbReview.ride_id == ride_id)
    if reviewer_id is not None:
        query = query.filter(DbReview.reviewer_id == reviewer_id)
    if reviewee_id is not None:
        query = query.filter(DbReview.reviewee_id == reviewee_id)

    reviews = query.all()

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for the given criteria.")

    return reviews



# 📌 Get a specific review by ID
@router.get("/{id}", response_model=ReviewDisplay)
def get_review(id: int, db: Session = Depends(get_db)):
    review = db_review.get_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found for this id.")
    return review


# 📌 Update a review
@router.put("/{id}", response_model=ReviewDisplay)
def update_review(
    id: int,
    request: ReviewBase = Depends(),  # ✅ Changed to support form data
    db: Session = Depends(get_db),
    file: Optional[UploadFile] = None  # ✅ Added support for file upload
):
    review = db.query(DbReview).filter(DbReview.id == id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found for this id.")
    
    # ✅ If a file is uploaded, determine the new file's URL
    media_url = review.media_url  # Keep the existing value
    if file:
        media_url = f"/uploads/{file.filename}"  # ✅ Directory where the file will be saved

    # ✅ Update only the fields provided in the request
    review.ride_id = request.ride_id
    review.reviewer_id = request.reviewer_id
    review.reviewee_id = request.reviewee_id
    review.review_type = request.review_type
    review.rating = request.rating
    review.comment = request.comment
    review.is_anonymous = request.is_anonymous
    review.media_url = media_url  # ✅ Now the file will be updated

    db.commit()
    db.refresh(review)
    
    return review



# 📌 Delete a review
@router.delete("/{id}", response_model=ReviewDeleteResponse)
def delete_review(id: int, db: Session = Depends(get_db)):
    deleted_review = db_review.delete_review(db, id)
    if not deleted_review:
        raise HTTPException(status_code=404, detail="Review not found or already deleted.")
    return ReviewDeleteResponse(message="Review successfully deleted.")
