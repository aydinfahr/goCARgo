from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Review, ReviewVote, User, Ride, Car
from schemas import ReviewCreate, ReviewUpdate, RideBase
from fastapi import HTTPException, status
from datetime import datetime, timedelta
try:
    from utils.sentiment_analysis import analyze_sentiment  # ✅ AI Sentiment Analysis for spam detection
except ImportError:
    raise ImportError("The module 'utils.sentiment_analysis' could not be resolved. Ensure it exists and is in the Python path.")

def create_ride(db: Session, request: RideBase):
    """
    ✅ Handles ride creation with proper validation and datetime handling.
    """

    # ✅ Ensure departure time is a valid datetime object
    departure_datetime = request.departure_time

    # ✅ Check if driver exists
    driver = db.query(User).filter(User.id == request.driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    # ✅ Check if car exists
    car = db.query(Car).filter(Car.id == request.car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found.")

    # ✅ Ensure the car belongs to the driver
    if car.owner_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver.")

    # ✅ Prevent duplicate rides with the same departure time
    existing_ride = db.query(Ride).filter(
        Ride.driver_id == request.driver_id,
        Ride.departure_time == departure_datetime
    ).first()
    if existing_ride:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A ride with the same details already exists.")

    # ✅ Prevent setting a past departure time
    if departure_datetime < datetime.now():
        raise HTTPException(status_code=400, detail="Departure time cannot be in the past.")

    # ✅ Validate price per seat
    if request.price_per_seat <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price per seat must be greater than zero.")

    # ✅ Validate seat count
    if request.total_seats < 1 or request.total_seats > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total seats must be between 1 and 4.")

    # ✅ Validate instant booking flag
    if not isinstance(request.instant_booking, bool):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid value for instant_booking.")

    # ✅ Create ride instance
    ride_data = request.model_dump()  # Convert the Pydantic model to a dictionary
    new_ride = Ride(**ride_data, available_seats=request.total_seats)

    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)

    return new_ride

def get_review_by_id(db: Session, review_id: int):
    """
    Fetches a review by its ID.

    Args:
        db (Session): The database session.
        review_id (int): The ID of the review.

    Returns:
        Review: The retrieved review object.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

def get_reviews_for_user(db: Session, user_id: int):
    """
    Retrieves all reviews for a specific user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[Review]: List of reviews for the user.
    """
    reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()

    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this user.")

    return reviews

def update_review(db: Session, review_id: int, review_update_data: ReviewUpdate):
    """
    Updates a review's content.

    Args:
        db (Session): The database session.
        review_id (int): The ID of the review to be updated.
        review_update_data (ReviewUpdate): The updated review data.

    Returns:
        Review: The updated review object.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    for key, value in review_update_data.dict(exclude_unset=True).items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    
    return review

def delete_review(db: Session, review_id: int):
    """
    Deletes a review from the database.

    Args:
        db (Session): The database session.
        review_id (int): The ID of the review to be deleted.

    Returns:
        dict: Confirmation message.
    """
    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()

    return {"message": "Review deleted successfully"}

def vote_review(db: Session, review_id: int, voter_id: int, vote_type: str):
    """
    Allows a user to vote (like/dislike) on a review.

    Args:
        db (Session): The database session.
        review_id (int): The ID of the review being voted on.
        voter_id (int): The ID of the user voting.
        vote_type (str): "like" or "dislike".

    Returns:
        dict: Confirmation message and updated vote counts.
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Prevent duplicate voting
    existing_vote = db.query(ReviewVote).filter(
        ReviewVote.review_id == review_id,
        ReviewVote.voter_id == voter_id
    ).first()

    if existing_vote:
        raise HTTPException(status_code=400, detail="You have already voted on this review.")

    # Add the vote
    new_vote = ReviewVote(
        review_id=review_id,
        voter_id=voter_id,
        vote_type=vote_type,
        created_at=datetime.utcnow()
    )

    db.add(new_vote)

    # Update like/dislike count
    if vote_type == "like":
        review.likes += 1
    elif vote_type == "dislike":
        review.dislikes += 1

    db.commit()
    db.refresh(review)

    return {
        "message": f"Vote recorded successfully: {vote_type}",
        "likes": review.likes,
        "dislikes": review.dislikes
    }

def update_user_rating(db: Session, user_id: int):
    """
    Updates the average rating of a user based on received reviews.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user whose rating needs updating.

    Returns:
        None
    """
    reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()
    if not reviews:
        return

    total_rating = sum(review.star_rating for review in reviews)
    average_rating = total_rating / len(reviews)

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.rating = round(average_rating, 2)
        user.rating_count = len(reviews)

    db.commit()
