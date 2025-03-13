# from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Text
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from sqlalchemy import Enum as SQLEnum  # ✅ SQLAlchemy Enum kullanımı düzeltildi
# from db.database import Base
# from db.enums import PaymentStatus, PaymentMethod, BookingStatus, ReviewCategory, ReviewVoteType, ComplaintStatus


# # ✅ User Model
# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     full_name = Column(String, nullable=False)
#     is_admin = Column(Boolean, default=False)
#     is_banned = Column(Boolean, default=False)
#     wallet_balance = Column(Float, default=100.0)
#     rating = Column(Float, default=0.0)
#     rating_count = Column(Integer, default=0)
#     verified_id = Column(Boolean, default=False)
#     verified_email = Column(Boolean, default=False)
#     agreed_terms = Column(Boolean, default=False)
#     member_since = Column(DateTime, default=func.now())

#     rides = relationship("Ride", back_populates="driver")
#     cars = relationship("Car", back_populates="owner")
#     bookings = relationship("Booking", back_populates="passenger")
#     reviews_written = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")
#     reviews_received = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")
#     payments = relationship("Payment", back_populates="user")


# # ✅ Ride Model
# class Ride(Base):
#     __tablename__ = "rides"

#     id = Column(Integer, primary_key=True, index=True)
#     driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
#     start_location = Column(String, nullable=False)
#     end_location = Column(String, nullable=False)
#     departure_time = Column(DateTime, nullable=False)
#     price_per_seat = Column(Float, nullable=False)
#     total_seats = Column(Integer, nullable=False)
#     available_seats = Column(Integer, nullable=False)
#     # status = Column(String, nullable=False, default="active")
#     instant_booking = Column(Boolean, default=False)

#     driver = relationship("User", back_populates="rides")
#     car = relationship("Car", back_populates="rides")
#     bookings = relationship("Booking", back_populates="ride")
#     payments = relationship("Payment", back_populates="ride")

# # ✅ Car Model
# class Car(Base):
#     __tablename__ = "cars"

#     id = Column(Integer, primary_key=True, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     brand = Column(String, nullable=False)
#     model = Column(String, nullable=False)
#     color = Column(String, nullable=False)
#     # plate_number = Column(String, nullable=False)    
#     # car_images = Column(String, nullable=True)

#     owner = relationship("User", back_populates="cars")
#     rides = relationship("Ride", back_populates="car")

# # ✅ Booking Model
# class Booking(Base):
#     __tablename__ = "bookings"

#     id = Column(Integer, primary_key=True, index=True)
#     ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
#     passenger_id = Column(Integer, ForeignKey("users.id"), nullable=True)
#     # phone_number = Column(String, nullable=True)
#     # booking_source = Column(String, nullable=False, default="online")
#     booking_time = Column(DateTime, default=func.now(), nullable=False)
#     status = Column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
#     seats_booked = Column(Integer, nullable=False)
#     # refund_amount = Column(Float, nullable=True)

#     ride = relationship("Ride", back_populates="bookings")
#     passenger = relationship("User", back_populates="bookings")

# # ✅ Payment Model
# class Payment(Base):
#     __tablename__ = "payments"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
#     amount = Column(Float, nullable=False)
#     payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
#     payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
#     charge_id = Column(String, nullable=True)  # ✅ Stripe için eklendi
#     payment_date = Column(DateTime, default=func.now())

#     user = relationship("User", back_populates="payments")
#     ride = relationship("Ride", back_populates="payments")

# # ✅ Review Model
# class Review(Base):
#     __tablename__ = "reviews"

#     id = Column(Integer, primary_key=True, index=True)
#     ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
#     reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     review_category = Column(SQLEnum(ReviewCategory), nullable=False)
#     star_rating = Column(Float, nullable=False)
#     review_text = Column(Text, nullable=True)
#     anonymous_review = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=func.now(), nullable=False)

#     likes = Column(Integer, default=0)
#     dislikes = Column(Integer, default=0)
#     reported = Column(Boolean, default=False)
#     hidden = Column(Boolean, default=False)

#     reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_written")
#     reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="reviews_received")
#     votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")
#     responses = relationship("ReviewResponse", back_populates="review", cascade="all, delete-orphan")

# # ✅ Review Response Model
# class ReviewResponse(Base):
#     __tablename__ = "review_responses"

#     id = Column(Integer, primary_key=True)
#     review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
#     responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     response_text = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=func.now(), nullable=False)

#     review = relationship("Review", back_populates="responses")
#     responder = relationship("User")

# # ✅ Review Vote Model
# class ReviewVote(Base):
#     __tablename__ = "review_votes"

#     id = Column(Integer, primary_key=True, index=True)
#     review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
#     voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     vote_type = Column(SQLEnum(ReviewVoteType), nullable=False)
#     created_at = Column(DateTime, default=func.now(), nullable=False)

#     review = relationship("Review", back_populates="votes")

# # # ✅ Complaint Model
# # class Complaint(Base):
# #     __tablename__ = "complaints"

# #     id = Column(Integer, primary_key=True, index=True)
# #     reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
# #     reporter_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
# #     review_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)
# #     reason = Column(Text, nullable=False)
# #     status = Column(SQLEnum(ComplaintStatus), default=ComplaintStatus.PENDING, nullable=False)
# #     created_at = Column(DateTime, default=func.now(), nullable=False)

# #     reported_user = relationship("User", foreign_keys=[reported_user_id])
# #     reporter_user = relationship("User", foreign_keys=[reporter_user_id])
# #     review = relationship("Review", foreign_keys=[review_id])


from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum  # ✅ SQLAlchemy Enum kullanımı düzeltildi
from db.database import Base
from db.enums import PaymentStatus, PaymentMethod, BookingStatus, ReviewCategory, ReviewVoteType, ComplaintStatus


# ✅ User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    wallet_balance = Column(Float, default=100.0)
    average_rating = Column(Float, default=0.0)  # ✅ New column to store average rating
    rating_count = Column(Integer, default=0)
    verified_id = Column(Boolean, default=False)
    verified_email = Column(Boolean, default=False)
    agreed_terms = Column(Boolean, default=False)
    member_since = Column(DateTime, default=func.now())

    rides = relationship("Ride", back_populates="driver")
    cars = relationship("Car", back_populates="owner")
    bookings = relationship("Booking", back_populates="passenger")
    reviews_written = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")
    payments = relationship("Payment", back_populates="user")


# ✅ Ride Model
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
    available_seats = Column(Integer, nullable=False)
    instant_booking = Column(Boolean, default=False)

    driver = relationship("User", back_populates="rides")
    car = relationship("Car", back_populates="rides")
    bookings = relationship("Booking", back_populates="ride")
    payments = relationship("Payment", back_populates="ride")

# ✅ Car Model
class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)

    owner = relationship("User", back_populates="cars")
    rides = relationship("Ride", back_populates="car")

# ✅ Booking Model
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    booking_time = Column(DateTime, default=func.now(), nullable=False)
    status = Column(SQLEnum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    seats_booked = Column(Integer, nullable=False)

    ride = relationship("Ride", back_populates="bookings")
    passenger = relationship("User", back_populates="bookings")

# ✅ Payment Model
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    charge_id = Column(String, nullable=True)
    payment_date = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="payments")
    ride = relationship("Ride", back_populates="payments")

# ✅ Review Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_category = Column(SQLEnum(ReviewCategory), nullable=False)
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
    responses = relationship("ReviewResponse", back_populates="review", cascade="all, delete-orphan")

# ✅ Review Response Model
class ReviewResponse(Base):
    __tablename__ = "review_responses"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    review = relationship("Review", back_populates="responses")
    responder = relationship("User")

# ✅ Review Vote Model
class ReviewVote(Base):
    __tablename__ = "review_votes"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    voter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vote_type = Column(SQLEnum(ReviewVoteType), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    review = relationship("Review", back_populates="votes")
