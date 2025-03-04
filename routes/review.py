# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from db import db_review, database
# from schemas import ReviewCreate, ReviewResponse

# router = APIRouter(
#     prefix="/review",
#     tags=["Review"]
# )

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


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import db_review, database
from schemas import ReviewCreate, ReviewResponse

router = APIRouter(
    prefix="/review",
    tags=["Review"]
)

@router.post("/", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(database.get_db)):
    return db_review.create_review(db, review)

@router.get("/ride/{ride_id}", response_model=list[ReviewResponse])
def get_reviews_by_ride(ride_id: int, db: Session = Depends(database.get_db)):
    return db_review.get_reviews_by_ride(db, ride_id)

@router.get("/user/{user_id}", response_model=list[ReviewResponse])
def get_reviews_by_user(user_id: int, db: Session = Depends(database.get_db)):
    return db_review.get_reviews_by_user(db, user_id)

@router.get("/reviewer/{reviewer_id}", response_model=list[ReviewResponse])
def get_reviews_by_reviewer(reviewer_id: int, db: Session = Depends(database.get_db)):
    return db_review.get_reviews_by_reviewer(db, reviewer_id)
