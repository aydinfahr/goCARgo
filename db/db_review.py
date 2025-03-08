from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Review, ReviewVote, User
from schemas import ReviewCreate, ReviewUpdate
from fastapi import HTTPException
from datetime import datetime, timedelta
try:
    from utils.sentiment_analysis import analyze_sentiment  # ✅ AI Sentiment Analysis for spam detection
except ImportError:
    raise ImportError("The module 'utils.sentiment_analysis' could not be resolved. Ensure it exists and is in the Python path.")

def create_review(db: Session, review_data: ReviewCreate):
    """
    Creates a new review for a ride, driver, passenger, or service.

    Args:
        db (Session): The database session.
        review_data (ReviewCreate): Review creation schema.

    Returns:
        Review: The created review object.
    """

    # Check if the reviewer and reviewee exist
    reviewer = db.query(User).filter(User.id == review_data.reviewer_id).first()
    reviewee = db.query(User).filter(User.id == review_data.reviewee_id).first()

    if not reviewer or not reviewee:
        raise HTTPException(status_code=404, detail="Reviewer or reviewee not found.")

    if reviewer.id == reviewee.id:
        raise HTTPException(status_code=400, detail="You cannot review yourself.")

    # ✅ Check if the same review already exists (Prevent duplicate reviews)
    existing_review = db.query(Review).filter(
        Review.ride_id == review_data.ride_id,
        Review.reviewer_id == review_data.reviewer_id,
        Review.reviewee_id == review_data.reviewee_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this ride/user.")

    # ✅ AI Sentiment Analysis Check (Blocks Fake or Abusive Reviews)
    if analyze_sentiment(review_data.review_text):
        raise HTTPException(status_code=400, detail="Review contains abusive or spam content.")

    new_review = Review(
        ride_id=review_data.ride_id,
        reviewer_id=review_data.reviewer_id,
        reviewee_id=review_data.reviewee_id,
        review_category=review_data.review_category,
        star_rating=review_data.star_rating,
        review_text=review_data.review_text,
        anonymous_review=review_data.anonymous_review,
        created_at=datetime.utcnow()
    )

    db.add(new_review)

    try:
        db.commit()
        db.refresh(new_review)
        
        # ✅ Update Reviewee's Average Rating
        update_user_rating(db, review_data.reviewee_id)
        
        return new_review
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Review could not be created due to integrity constraints.")

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
