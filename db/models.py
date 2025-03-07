from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


# ✅ USER MODEL: Represents a platform user
class DbUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    rating = Column(Float, nullable=True)  # User's overall rating (based on received reviews)
    verified_id = Column(Boolean, default=False)  # Indicates if ID is verified
    verified_email = Column(Boolean, default=False)  # Indicates if email is verified
    bio = Column(String, nullable=True)  # User's bio (optional)
    member_since = Column(DateTime, default=func.now())  # Account creation timestamp
    is_admin = Column(Boolean, default=False)  # Admin status

    # ✅ Relationships
    rides = relationship("DbRide", back_populates="driver")  # Rides offered by the user
    cars = relationship("DbCar", back_populates="owner")  # Cars owned by the user
    bookings = relationship("DbBooking", back_populates="passenger")  # Bookings made by the user
    reviews_written = relationship("DbReview", foreign_keys="[DbReview.reviewer_id]", back_populates="reviewer")
    reviews_received = relationship("DbReview", foreign_keys="[DbReview.reviewee_id]", back_populates="reviewee")


# ✅ CAR MODEL: Represents a car owned by a user
class DbCar(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)  # Car brand (e.g., Toyota)
    model = Column(String, nullable=False)  # Car model (e.g., Corolla)
    color = Column(String, nullable=False)  # Car color (e.g., Red)

    # ✅ Relationships
    owner = relationship("DbUser", back_populates="cars")  # The user who owns the car
    rides = relationship("DbRide", back_populates="car")  # Rides using this car


# ✅ RIDE MODEL: Represents a car-sharing ride offered by a user
class DbRide(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The driver offering the ride
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)  # The car used for the ride
    start_location = Column(String, nullable=False)  # Ride starting point
    end_location = Column(String, nullable=False)  # Ride destination
    departure_time = Column(DateTime, nullable=False)  # Departure time
    price_per_seat = Column(Float, nullable=False)  # Cost per seat
    total_seats = Column(Integer, nullable=False)  # Total available seats

    # ✅ Relationships
    driver = relationship("DbUser", back_populates="rides")
    car = relationship("DbCar", back_populates="rides")
    bookings = relationship("DbBooking", back_populates="ride")
    reviews = relationship("DbReview", back_populates="ride")  # Reviews related to this ride


# ✅ BOOKING MODEL: Represents a user's booking for a ride
class DbBooking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)  # The ride being booked
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The passenger making the booking
    booking_time = Column(DateTime, default=func.now(), nullable=False)  # Timestamp of booking
    status = Column(String, default="Pending")  # Booking status (Pending, Confirmed, Canceled)
    seats_booked = Column(Integer, nullable=False)  # Number of seats booked

    # ✅ Relationships
    ride = relationship("DbRide", back_populates="bookings")
    passenger = relationship("DbUser", back_populates="bookings")


# ✅ REVIEW MODEL: Stores user feedback about rides, drivers, passengers, and cars
class DbReview(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)  # Ride being reviewed
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User writing the review
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # User receiving the review
    review_type = Column(String, nullable=False)  # "driver", "passenger", "car", "service"
    rating = Column(Float, nullable=False)  # Rating (1.0-5.0)
    comment = Column(String, nullable=True)  # Optional comment
    is_anonymous = Column(Boolean, default=False)  # Indicates if the review is anonymous
    media_url = Column(String, nullable=True)  # URL for any attached media (image/video)
    review_time = Column(DateTime, default=func.now(), nullable=False)  # Timestamp of the review

    # ✅ Like & Dislike Counters
    likes = Column(Integer, default=0)  # Stores number of likes
    dislikes = Column(Integer, default=0)  # Stores number of dislikes

    # ✅ Relationships
    ride = relationship("DbRide", back_populates="reviews")
    reviewer = relationship("DbUser", foreign_keys=[reviewer_id], back_populates="reviews_written")
    reviewee = relationship("DbUser", foreign_keys=[reviewee_id], back_populates="reviews_received")
    votes = relationship("DbReviewVote", back_populates="review", cascade="all, delete-orphan")  # Likes/Dislikes
    responses = relationship("DbReviewResponse", back_populates="review", cascade="all, delete-orphan")  # Replies


# ✅ REVIEW RESPONSE MODEL: Allows users to respond to reviews
class DbReviewResponse(Base):
    __tablename__ = "review_responses"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)  # The review being responded to
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The user responding
    response_text = Column(String, nullable=False)  # Response content
    response_time = Column(DateTime, default=func.now(), nullable=False)  # Timestamp of response

    # ✅ Relationships
    review = relationship("DbReview", back_populates="responses")
    responder = relationship("DbUser")


# ✅ REVIEW VOTE MODEL: Stores user votes (likes/dislikes) for reviews
class DbReviewVote(Base):
    __tablename__ = "review_votes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)  # The review being voted on
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The user who voted
    vote_type = Column(String, nullable=False)  # "like" or "dislike"

    # Prevent duplicate votes by the same user on the same review
    __table_args__ = (UniqueConstraint("review_id", "user_id", name="unique_review_vote"),)

    # ✅ Relationships
    review = relationship("DbReview", back_populates="votes")
