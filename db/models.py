from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base



class DbReview(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_type = Column(String, nullable=False)  # ✅ "driver", "passenger", "car", "service"
    rating = Column(Float, nullable=False)
    comment = Column(String, nullable=True)
    is_anonymous = Column(Boolean, default=False)  # ✅ Controling anonymous or not
    media_url = Column(String, nullable=True)  # ✅ Store image/video URL
    likes = Column(Integer, default=0)  # Did users find this review helpful count number?
    dislike = Column(Integer, default=0)  # Did users find this review unnecessary count number?
    review_time = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    ride = relationship("DbRide", back_populates="reviews")
    #user = relationship("DbUser", foreign_keys=[user_id])  
    reviewer = relationship("DbUser", foreign_keys=[reviewer_id], back_populates="reviews_written")
    reviewee = relationship("DbUser", foreign_keys=[reviewee_id], back_populates="reviews_received")
    responses = relationship("DbReviewResponse", back_populates="review")
    votes = relationship("DbReviewVote", back_populates="review", cascade="all, delete-orphan")

    # No relationship needed for review_type as it is a simple string column


class DbReviewResponse(Base):
    __tablename__ = "review_responses"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The user replying
    response_text = Column(String, nullable=False)
    response_time = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    review = relationship("DbReview", back_populates="responses")
    responder = relationship("DbUser")


class DbReviewVote(Base):
    """Stores likes/dislikes for reviews with a unique constraint to prevent duplicate votes."""
    __tablename__ = "review_votes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_type = Column(String, nullable=False)  # "like" or "dislike"

    # Prevent a user from voting multiple times on the same review
    __table_args__ = (UniqueConstraint("review_id", "user_id", name="unique_review_vote"),)

    # Relationships
    review = relationship("DbReview", back_populates="votes")


class DbUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    rating = Column(Float, nullable=True)
    verified_id = Column(Boolean, default=False)
    verified_email = Column(Boolean, default=False)
    bio = Column(String, nullable=True)
    member_since = Column(DateTime, default=func.now())
    is_admin = Column(Boolean, default=False)

    # Relationships
    rides = relationship("DbRide", back_populates="driver")
    cars = relationship("DbCar", back_populates="owner")
    bookings = relationship("DbBooking", back_populates="passenger")
    reviews_written = relationship("DbReview", foreign_keys=[DbReview.reviewer_id], back_populates="reviewer")
    reviews_received = relationship("DbReview", foreign_keys=[DbReview.reviewee_id], back_populates="reviewee")




class DbCar(Base):
    """Represents a car owned by a user."""
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)

    # Relationships
    owner = relationship("DbUser", back_populates="cars")
    rides = relationship("DbRide", back_populates="car")


class DbRide(Base):
    """Represents a ride offered by a user."""
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    start_location = Column(String, nullable=False)
    end_location = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)

    # Relationships
    driver = relationship("DbUser", back_populates="rides")
    car = relationship("DbCar", back_populates="rides")
    bookings = relationship("DbBooking", back_populates="ride")
    reviews = relationship("DbReview", back_populates="ride")


class DbBooking(Base):
    """Represents a booking made by a user for a ride."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_time = Column(DateTime, default=func.now(), nullable=False)
    status = Column(String, default="Pending")
    seats_booked = Column(Integer, nullable=False)

    # Relationships
    ride = relationship("DbRide", back_populates="bookings")
    passenger = relationship("DbUser", back_populates="bookings")


