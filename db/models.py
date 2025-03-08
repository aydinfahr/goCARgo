from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Enum, Text
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()

# ✅ ENUM Tanımları (SQLAlchemy Enum Kullanımıyla)
class UserRole(enum.Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"
    ADMIN = "admin"

class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

class ReviewCategory(enum.Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"
    CAR = "car"
    SERVICE = "service"

class VoteType(enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# ✅ Kullanıcı Modeli
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole, name="user_roles"), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    wallet_balance = Column(Float, default=0.0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    verified_id = Column(Boolean, default=False)
    verified_email = Column(Boolean, default=False)
    agreed_terms = Column(Boolean, default=False)  # ✅ Kullanıcı sözleşmesini onaylama alanı
    member_since = Column(DateTime, default=func.now())

    rides = relationship("Ride", back_populates="driver")
    cars = relationship("Car", back_populates="owner")
    bookings = relationship("Booking", back_populates="passenger")
    reviews_written = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")
    payments = relationship("Payment", back_populates="user")

# ✅ Yolculuk Modeli
class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    start_location = Column(String, nullable=False)
    end_location = Column(String, nullable=False)
    departure_time = Column(DateTime, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)

    driver = relationship("User", back_populates="rides")
    car = relationship("Car", back_populates="rides")
    bookings = relationship("Booking", back_populates="ride")
    payments = relationship("Payment", back_populates="ride")

# ✅ Araba Modeli
class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)
    car_images = Column(String, nullable=True)

    owner = relationship("User", back_populates="cars")
    rides = relationship("Ride", back_populates="car")

# ✅ Rezervasyon Modeli
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    phone_number = Column(String, nullable=True)
    booking_source = Column(Enum("online", "offline", name="booking_sources"), default="online")  
    booking_time = Column(DateTime, default=func.now(), nullable=False)
    status = Column(Enum(BookingStatus, name="booking_statuses"), default=BookingStatus.PENDING)
    seats_booked = Column(Integer, nullable=False)
    refund_amount = Column(Float, nullable=True)

    ride = relationship("Ride", back_populates="bookings")
    passenger = relationship("User", back_populates="bookings", foreign_keys=[passenger_id])

# ✅ Yorum Modeli
# ✅ Review Yanıt Modeli
class ReviewResponse(Base):
    __tablename__ = "review_responses"
    
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    review = relationship("Review", back_populates="responses")
    responder = relationship("User")

# ✅ Review modeline `responses` ilişkilendirmesi eklendi mi?
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_category = Column(Enum("driver", "passenger", "car", "service"), nullable=False)
    star_rating = Column(Float, nullable=False)
    review_text = Column(Text, nullable=True)
    anonymous_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    reported = Column(Boolean, default=False)
    hidden = Column(Boolean, default=False)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_written")
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")
    votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")
    responses = relationship("ReviewResponse", back_populates="review", cascade="all, delete-orphan")  # 🔥 Eksikse ekle!


# ✅ Yorum Oylama Modeli
class ReviewVote(Base):
    __tablename__ = "review_votes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_type = Column(Enum(VoteType, name="vote_types"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    review = relationship("Review", back_populates="votes")

# ✅ Kullanıcı Şikayet Modeli
class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(Enum("pending", "resolved", "dismissed", name="complaint_statuses"), default="pending", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    reported_user = relationship("User", foreign_keys=[reported_user_id])
    reporter_user = relationship("User", foreign_keys=[reporter_user_id])
    review = relationship("Review", foreign_keys=[review_id])

# ✅ Ödeme Modeli
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(Enum(PaymentStatus, name="payment_statuses"), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="payments")
    ride = relationship("Ride", back_populates="payments")
