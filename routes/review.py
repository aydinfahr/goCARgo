from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import db_review, database
from schemas import ReviewDisplay, ReviewBase, ReviewDeleteResponse
from typing import List, Optional
from db.models import DbReview
from db.database import get_db

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

# @router.post("/", response_model=ReviewResponse)
# def create_review(review: ReviewCreate, db: Session = Depends(database.get_db)):
#     return db_review.create_review(db, review)

# @router.get("/ride/{ride_id}", response_model=list[ReviewResponse])
# def get_reviews_by_ride(ride_id: int, db: Session = Depends(database.get_db)):
#     return db_review.get_reviews_by_ride(db, ride_id)

# @router.get("/user/{user_id}", response_model=list[ReviewResponse])
# def get_reviews_by_user(user_id: int, db: Session = Depends(database.get_db)):
#     return db_review.get_reviews_by_user(db, user_id)

# @router.get("/reviewer/{reviewer_id}", response_model=list[ReviewResponse])
# def get_reviews_by_reviewer(reviewer_id: int, db: Session = Depends(database.get_db)):
#     return db_review.get_reviews_by_reviewer(db, reviewer_id)


# Create a new review
@router.post("/", response_model=ReviewDisplay)
def create_review(request: ReviewBase, db: Session = Depends(get_db)):
    try:
        print(f"Received request: {request}")  # Debugging print

        # Check if the same review already exists
        existing_review = db.query(DbReview).filter(
            DbReview.ride_id == request.ride_id,
            DbReview.user_id == request.user_id,
            DbReview.reviewer_id == request.reviewer_id,
            DbReview.reviewee_id == request.reviewee_id
        ).first()

        if existing_review:
            raise HTTPException(status_code=400, detail="Review already exists for this ride and user.")

        # Create a new review instance
        new_review = DbReview(**request.dict())

        # Add to database
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



# # Get all reviews (optional filters)
# @router.get("/", response_model=List[ReviewDisplay])
# def get_reviews(ride_id: int = None, user_id: int = None, reviewer_id: int = None, db: Session = Depends(get_db)):
#     return db_review.get_reviews(db, ride_id, user_id, reviewer_id)


@router.get("/", response_model=List[ReviewDisplay])
def get_reviews(
    ride_id: Optional[int] = None,
    user_id: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Query reviews based on optional filters
    query = db.query(DbReview)

    if ride_id is not None:
        query = query.filter(DbReview.ride_id == ride_id)
    if user_id is not None:
        query = query.filter(DbReview.user_id == user_id)
    if reviewer_id is not None:
        query = query.filter(DbReview.reviewer_id == reviewer_id)

    reviews = query.all()

    # If no reviews are found, return 404 Not Found
    if not reviews:
        raise HTTPException(status_code=404, detail="Review not found for this id.")

    return reviews

# Get a specific review by ID
@router.get("/{id}", response_model=ReviewDisplay)
def get_review(id: int, db: Session = Depends(get_db)):
    review = db_review.get_review_by_id(db, id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found for this id.")
    return review

# Update a review
@router.put("/{id}", response_model=ReviewDisplay)
def update_review(id: int, request: ReviewBase, db: Session = Depends(get_db)):
    updated_review = db_review.update_review(db, id, request)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found for this id.")
    return updated_review

# Delete a review
@router.delete("/{id}", response_model=ReviewDeleteResponse)
def delete_review(id: int, db: Session = Depends(get_db)):
    deleted_review = db_review.delete_review(db, id)
    if not deleted_review:
        raise HTTPException(status_code=404, detail="Review not found or already deleted.")
    return ReviewDeleteResponse(message="Review successfully deleted.")