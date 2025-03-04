from sqlalchemy.orm import Session
from db import models
from schemas import ReviewCreate
from fastapi import HTTPException

# def create_review(db: Session, review: ReviewCreate):
#     db_review = models.DbReview(**review.dict())
#     db.add(db_review)
#     db.commit()
#     db.refresh(db_review)
#     return db_review

# def get_reviews_by_ride(db: Session, ride_id: int):
#     return db.query(models.DbReview).filter(models.DbReview.ride_id == ride_id).all()

# def get_reviews_by_user(db: Session, user_id: int):
#     return db.query(models.DbReview).filter(models.DbReview.reviewee_id == user_id).all()

# def get_reviews_by_reviewer(db: Session, reviewer_id: int):
#     return db.query(models.DbReview).filter(models.DbReview.reviewer_id == reviewer_id).all()


def create_review(db: Session, review: ReviewCreate):
    # Kullanıcının bu yolculukta olup olmadığını kontrol et
    ride = db.query(models.DbRide).filter(models.DbRide.id == review.ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # Kullanıcının yolculukta olup olmadığını kontrol et
    ride_passengers = [p.id for p in ride.passengers]  # ride içindeki yolcular
    if review.reviewee_id not in ride_passengers and review.reviewee_id != ride.driver_id:
        raise HTTPException(status_code=400, detail="User is not part of this ride")

    db_review = models.DbReview(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews_by_ride(db: Session, ride_id: int):
    return db.query(models.DbReview).filter(models.DbReview.ride_id == ride_id).all()

def get_reviews_by_user(db: Session, user_id: int):
    return db.query(models.DbReview).filter(models.DbReview.reviewee_id == user_id).all()

def get_reviews_by_reviewer(db: Session, reviewer_id: int):
    return db.query(models.DbReview).filter(models.DbReview.reviewer_id == reviewer_id).all()