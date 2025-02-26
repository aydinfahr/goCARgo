
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class DbUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)  # Unique email for login
    password = Column(String, nullable=False)     # Encrypted password
    full_name = Column(String, nullable=False)           # User's full name
    rating = Column(Float, nullable=True)                  # Average rating (1-5)
    verified_id = Column(Boolean, default=False)         # Verified ID status
    verified_email = Column(Boolean, default=False)      # Verified email status
    bio = Column(String, nullable=True)                  # Short description (multilingual support possible)
    member_since = Column(DateTime, default=func.now())  # Account creation date
    is_admin = Column(Boolean, default=False)            # Admin role 
    
    # Optional fields (Not in BlaBlaCar, but useful)
    # profile_picture = Column(String, nullable=True)      # Profile image URL
    # is_active = Column(Boolean, default=True)            # Account activation status
    # experience_level = Column(String, nullable=True)     # Example: "Newbie", "Ambassador"
    # driving_skills = Column(Integer, default=None)       # Example: 3/3 driving skills
    # prefers_chatty = Column(Boolean, nullable=True)      # Whether the user likes to chat during rides
    # phone_number = Column(String, nullable=True)         # BlaBlaCar does not show phone numbers
    # ride_count = Column(Integer, default=0)              # Can be calculated dynamically
    
    # Relationships
    rides = relationship("DbRide", back_populates="driver")  
    cars = relationship("DbCar", back_populates="owner")  
    bookings = relationship("DbBooking", back_populates="passenger")  
    reviews_written = relationship("DbReview", foreign_keys="DbReview.reviewer_id", back_populates="reviewer")
    reviews_received = relationship("DbReview", foreign_keys="DbReview.reviewee_id", back_populates="reviewee")


class DbCar(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The user who owns the car
    brand = Column(String, nullable=False)  # Example: Toyota, BMW
    model = Column(String, nullable=False)  # Example: Corolla, X5
    color = Column(String, nullable=False)  # Example: Red, Black
    
    # Optional fields (Not in BlaBlaCar, but useful)
    # year = Column(Integer, nullable=False)  # Example: 2020, 2023
    # seats = Column(Integer, nullable=False)  # Total seats available
    # luggage_capacity = Column(Integer, nullable=False)  # Luggage space available
    # car_picture = Column(String, nullable=True)  # URL to car image
    # air_conditioning = Column(Boolean, default=True)  # Does the car have AC?
    # comfort_level = Column(String, nullable=False)  # Example: Economy, Luxury
    # license_plate = Column(String, unique=True, nullable=True)  # BlaBlaCar does not display this
    # is_verified = Column(Boolean, default=False)  # If car verification is needed
    
    # Relationships
    owner = relationship("DbUser", back_populates="cars")  
    rides = relationship("DbRide", back_populates="car") 


class DbRide(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Driver of the ride
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)  # Car used for the ride
    start_location = Column(String, nullable=False)  # Example: "Den Haag"
    end_location = Column(String, nullable=False)  # Example: "Amsterdam"
    departure_time = Column(DateTime, nullable=False)  # Example: "2025-02-27 06:30"
    price_per_seat = Column(Float, nullable=False)  # Cost per seat                         # default=0.00 ?
    total_seats = Column(Integer, nullable=False)  # Seats available for passengers #total_seats yap

    # Optional fields (Not in BlaBlaCar, but useful)
    # luggage_capacity = Column(Integer, nullable=False)  # Luggage space per passenger
    # max_passengers_in_back = Column(Integer, nullable=True)  # Max number of people in the backseat
    # smoking_allowed = Column(Boolean, default=False)  # If smoking is allowed
    # is_verified = Column(Boolean, default=False)  # If the ride is verified
    # ride_duration = Column(Integer, nullable=True)  # Can be calculated dynamically
    # ride_status = Column(String, default="Scheduled")  # Scheduled, Ongoing, Completed, Canceled

    # Relationships
    driver = relationship("DbUser", back_populates="rides")  
    car = relationship("DbCar", back_populates="rides")  
    bookings = relationship("DbBooking", back_populates="ride")  
    reviews = relationship("DbReview", back_populates="ride")  


class DbBooking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)  # Reference to the ride
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Reference to the passenger
    booking_time = Column(DateTime, default=func.now(), nullable=False)  # Timestamp of booking
    status = Column(String, default="Pending")  # Status: Pending, Accepted, Rejected, Canceled
    seats_booked = Column(Integer, nullable=False)  # Number of seats booked

    # Optional fields (Not in BlaBlaCar, but useful)
    # payment_status = Column(String, nullable=True)  # Example: Paid, Unpaid, Refunded
    # cancellation_reason = Column(String, nullable=True)  # Reason for cancellation

    # Relationships
    ride = relationship("DbRide", back_populates="bookings")  
    passenger = relationship("DbUser", back_populates="bookings")


class DbReview(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)  # Reference to the ride
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who wrote the review
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who is being reviewed
    rating = Column(Float, nullable=False)  # Rating (1-5 stars)
    comment = Column(String, nullable=True)  # Optional feedback text
    review_time = Column(DateTime, default=func.now(), nullable=False)  # Timestamp of review

    # Relationships
    ride = relationship("DbRide", back_populates="reviews")  
    reviewer = relationship("DbUser", foreign_keys=[reviewer_id], back_populates="reviews_written")  
    reviewee = relationship("DbUser", foreign_keys=[reviewee_id], back_populates="reviews_received")  