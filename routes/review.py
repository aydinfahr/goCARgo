from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from db import db_review
from schemas import ReviewDisplay, ReviewBase, ReviewDeleteResponse, ReviewVoteBase, ReviewVoteDisplay, ReviewVoteCount
from typing import List, Optional
from db.models import DbReview, DbReviewVote
from db.database import get_db
from enum import Enum  # ✅ Import Enum for dropdown options


# ✅ Define FastAPI router for review-related endpoints
router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


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


# ==============================================================
# 📌 CREATE A NEW REVIEW (WITH FILE UPLOAD SUPPORT)
# ==============================================================
# @router.post("/", response_model=ReviewDisplay)
# def create_review(
#     ride_id: int = Form(...),
#     reviewer_id: int = Form(...),
#     reviewee_id: int = Form(...),
#     review_type: ReviewType = Form(...),  # ✅ Uses dropdown selection
#     rating: float = Form(...),
#     comment: Optional[str] = Form(None),
#     is_anonymous: bool = Form(False),
#     file: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     Creates a new review for a ride, driver, passenger, or service.
#     - Prevents duplicate reviews for the same ride.
#     - Allows optional file uploads (e.g., images/videos).
#     """

#     # ✅ Check if the same review already exists
#     existing_review = db.query(DbReview).filter(
#         DbReview.ride_id == ride_id,
#         DbReview.reviewer_id == reviewer_id,
#         DbReview.reviewee_id == reviewee_id
#     ).first()

#     if existing_review:
#         raise HTTPException(status_code=400, detail="Review already exists for this ride and user.")

#     # ✅ Handle file upload (save file path)
#     media_url = None
#     if file:
#         media_url = f"/uploads/{file.filename}"  # Example: Store the file path

#     # ✅ Create a new review instance
#     new_review = DbReview(
#         ride_id=ride_id,
#         reviewer_id=reviewer_id,
#         reviewee_id=reviewee_id,
#         review_type=review_type.value,  # Store the string value
#         rating=rating,
#         comment=comment,
#         is_anonymous=is_anonymous,
#         media_url=media_url
#     )

#     # ✅ Add to database
#     db.add(new_review)
#     db.commit()
#     db.refresh(new_review)

#     return new_review


@router.post("/", response_model=ReviewDisplay)
def create_review(
    ride_id: int = Form(...),
    reviewer_id: int = Form(...),
    reviewee_id: int = Form(...),
    review_type: ReviewType = Form(...),  # ✅ Uses dropdown selection
    rating: float = Form(...),
    comment: Optional[str] = Form(None),
    is_anonymous: bool = Form(False),
    file: Optional[UploadFile] = File(None),  # ✅ Optional file parameter
    db: Session = Depends(get_db)
):
    """
    Creates a new review for a ride, driver, passenger, or service.
    - Prevents duplicate reviews for the same ride.
    - Allows optional file uploads (e.g., images/videos).
    """

    # ✅ Ensure file is truly optional
    media_url = None
    if file and file.filename:  # ✅ Only process if file is uploaded
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
        media_url=media_url  # ✅ Store media file URL
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
    """

    # ✅ Check if review exists
    review = db.query(DbReview).filter(DbReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

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
    - Includes the number of likes and dislikes.
    """

    # ✅ Ensure at least one filter is provided
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
    
    # ✅ Calculate like & dislike counts for each review
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

        # Convert ORM object to dict and add vote_count field
        review_dict = review.__dict__
        review_dict["vote_count"] = ReviewVoteCount(likes=like_count, dislikes=dislike_count)
        review_list.append(review_dict)

    return reviews


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
