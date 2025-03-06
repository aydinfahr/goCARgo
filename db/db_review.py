from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from db.models import DbReview  # Sadece ihtiyacın olan modeli import et
from schemas import ReviewBase, ReviewUpdate
import db.models  # Tüm modelleri import et
db.models.DbReview






# def create_review(db: Session, review: ReviewCreate):
#     # Kullanıcının bu yolculukta olup olmadığını kontrol et
#     ride = db.query(models.DbRide).filter(models.DbRide.id == review.ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found")

#     # Kullanıcının yolculukta olup olmadığını kontrol et
#     ride_passengers = [p.id for p in ride.passengers]  # ride içindeki yolcular
#     if review.reviewee_id not in ride_passengers and review.reviewee_id != ride.driver_id:
#         raise HTTPException(status_code=400, detail="User is not part of this ride")

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



# Create a new review
def create_review(db: Session, review: ReviewBase):
    new_review = DbReview(**review.dict())  # Convert schema to ORM model
    db.add(new_review)
    db.commit()
    db.refresh(new_review)  # Refresh to get the new ID
    return new_review

# Get all reviews with optional filters
def get_reviews(db: Session, ride_id: int = None, user_id: int = None, reviewer_id: int = None):
    # Start a base query with joinedload to fetch related user, reviewer, and ride data
    query = db.query(DbReview).options(
        joinedload(DbReview.user), 
        joinedload(DbReview.reviewer), 
        joinedload(DbReview.ride)
    )

    # Apply filters only if parameters are provided
    if ride_id:
        query = query.filter(DbReview.ride_id == ride_id)
    if user_id:
        query = query.filter(DbReview.user_id == user_id)
    if reviewer_id:
        query = query.filter(DbReview.reviewer_id == reviewer_id)

    return query.all()

# Get a single review by ID
def get_review_by_id(db: Session, review_id: int):
    return db.query(DbReview).options(
        joinedload(DbReview.user), 
        joinedload(DbReview.reviewer), 
        joinedload(DbReview.ride)
    ).filter(DbReview.id == review_id).first()

# Update a review
def update_review(db: Session, review_id: int, review_data: ReviewUpdate):
    review = db.query(DbReview).filter(DbReview.id == review_id).first()
    
    if not review:
        return None  # Return None if the review does not exist

    for key, value in review_data.dict(exclude_unset=True).items():
        setattr(review, key, value)  # Update only provided fields

    db.commit()
    db.refresh(review)
    return review

# Delete a review
def delete_review(db: Session, review_id: int):
    review = db.query(DbReview).filter(DbReview.id == review_id).first()
    
    if not review:
        return None  # Return None if the review does not exist

    db.delete(review)
    db.commit()
    return review
