# from pydantic import BaseModel, EmailStr, Field
# from enum import Enum
# from typing import Optional, List
# from datetime import datetime
# from db.models import UserRole, ReviewCategory, ReviewVoteType
# PaymentStatus  # Import Enums from models.py
# from schemas import PaymentCreate, PaymentDisplay  # ✅ Eğer PaymentRequest kullanılmıyorsa bunu kaldır



# # ✅ User Schemas
# class UserBaseSchema(BaseModel):
#     username: str
#     email: EmailStr
#     password: str
#     full_name: str
#     role: UserRole  # Dropdown selection

# class UserCreate(UserBaseSchema):
#     agreed_terms: bool  # Checkbox for user agreement (True/False)

# class UserDisplay(BaseModel):
#     id: int
#     username: str
#     email: EmailStr
#     full_name: str
#     role: UserRole
#     is_admin: bool
#     is_banned: bool
#     rating: float
#     rating_count: int
#     verified_id: bool
#     verified_email: bool
#     member_since: datetime
#     profile_picture: Optional[str] = None  # Profile Image URL

#     class Config:
#         from_attributes = True  # Enables ORM mode for SQLAlchemy

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class UserUpdate(BaseModel):
#     username: Optional[str] = None
#     email: Optional[EmailStr] = None
#     full_name: Optional[str] = None
#     profile_picture: Optional[str] = None

# class UserDeleteResponse(BaseModel):
#     message: str

# # ✅ Car Schemas
# class CarBase(BaseModel):
#     brand: str
#     model: str
#     color: str
#     images: Optional[List[str]] = None  # Car images

# class CarCreate(CarBase):
#     pass  # No additional fields

# class CarDisplay(CarBase):
#     id: int
#     owner_id: int

#     class Config:
#         from_attributes = True

# class CarUpdate(BaseModel):
#     brand: Optional[str] = None
#     model: Optional[str] = None
#     color: Optional[str] = None
#     images: Optional[List[str]] = None

# # ✅ Ride Schemas
# class RideBase(BaseModel):
#     driver_id: int
#     car_id: int
#     start_location: str
#     end_location: str
#     departure_time: datetime
#     price_per_seat: float
#     total_seats: int

# class RideCreate(RideBase):
#     pass  # No additional fields

# class RideDisplay(RideBase):
#     id: int
#     available_seats: int

#     class Config:
#         from_attributes = True

# class RideUpdate(BaseModel):
#     start_location: Optional[str] = None
#     end_location: Optional[str] = None
#     departure_time: Optional[datetime] = None
#     price_per_seat: Optional[float] = None
#     total_seats: Optional[int] = None

# # ✅ Booking Schemas
# class BookingStatus(str, Enum):
#     PENDING = "pending"
#     CONFIRMED = "confirmed"
#     CANCELLED = "cancelled"

# class BookingBase(BaseModel):
#     ride_id: int
#     passenger_id: Optional[int]  # Only for online bookings
#     phone_number: Optional[str]  # Only for offline bookings
#     seats_booked: int

# class BookingCreate(BookingBase):
#     pass  # No additional fields

# class BookingDisplay(BaseModel):
#     id: int
#     ride_id: int
#     passenger_id: Optional[int] = None
#     phone_number: Optional[str] = None
#     booking_time: datetime
#     status: BookingStatus
#     seats_booked: int
#     refund_amount: Optional[float] = None

#     class Config:
#         from_attributes = True

# class BookingCancel(BaseModel):
#     booking_id: int
#     cancel_reason: Optional[str] = None  # Cancellation reason (optional)

# # ✅ Review Schemas
# class ReviewBase(BaseModel):
#     ride_id: int
#     author_id: int  # User who wrote the review
#     target_id: int  # User being reviewed
#     review_category: ReviewCategory  # Enum for review type
#     star_rating: float = Field(..., ge=1.0, le=5.0, description="Rating must be between 1 and 5")
#     review_text: Optional[str] = None
#     anonymous_review: bool = False
#     media_url: Optional[str] = None  # Image/Video URL

# class ReviewCreate(ReviewBase):
#     pass  # No additional fields

# class ReviewDisplay(ReviewBase):
#     id: int
#     created_at: datetime
#     likes: int
#     dislikes: int
#     average_rating: float  # Dynamically updated average rating

#     class Config:
#         from_attributes = True

# class ReviewVoteCreate(BaseModel):
#     review_id: int
#     voter_id: int
#     vote_type: ReviewVoteType
  # Enum: Like or Dislike

# class ReviewResponseCreate(BaseModel):
#     review_id: int
#     responder_id: int
#     response_text: str

# # ✅ Vote Schemas
# class ReviewVoteBase(BaseModel):
#     review_id: int
#     voter_id: int
#     vote_type: ReviewVoteType
  # Enum: Like or Dislike

# class ReviewVoteDisplay(BaseModel):
#     id: int
#     vote_type: ReviewVoteType

#     created_at: datetime

#     class Config:
#         from_attributes = True

# # ✅ Payment Schemas
# class PaymentBase(BaseModel):
#     user_id: int
#     ride_id: int
#     amount: float
#     payment_status: PaymentStatus

# class PaymentCreate(PaymentBase):
#     pass  # No additional fields

# class PaymentDisplay(BaseModel):
#     id: int
#     user_id: int
#     ride_id: int
#     amount: float
#     payment_status: PaymentStatus
#     payment_date: datetime

#     class Config:
#         from_attributes = True

# # ✅ Refund Policy Schema
# class RefundPolicy(BaseModel):
#     refund_percentage_24h: float = 1.0  # 100% refund if canceled 24+ hours before
#     refund_percentage_12h: float = 0.5  # 50% refund if canceled 12-24 hours before
#     refund_percentage_last_min: float = 0.0  # No refund if canceled less than 12 hours before

# # ✅ Authentication Schemas
# class AuthRequest(BaseModel):
#     email: EmailStr
#     password: str

# class AuthResponse(BaseModel):
#     access_token: str
#     token_type: str
#     user: UserDisplay

# # ✅ User Agreement Schema
# class Agreement(BaseModel):
#     agreed: bool  # Must be true to proceed with signup


from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from db.enums import (
    UserRole,
    ReviewCategory,
    ReviewVoteType,
    PaymentStatus,
    PaymentMethod,
    BookingStatus,
    ComplaintStatus
)



# ✅ User Schemas
class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole  # Dropdown selection

class UserCreate(UserBaseSchema):
    agreed_terms: bool  # Checkbox for user agreement (True/False)

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_admin: bool
    is_banned: bool
    rating: float
    rating_count: int
    verified_id: bool
    verified_email: bool
    member_since: datetime
    profile_picture: Optional[str] = None  # Profile Image URL

    class Config:
        from_attributes = True  # Enables ORM mode for SQLAlchemy

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserDeleteResponse(BaseModel):
    message: str

# ✅ Car Schemas
class CarBase(BaseModel):
    brand: str
    model: str
    color: str
    images: Optional[List[str]] = None  # Car images

class CarCreate(CarBase):
    pass  # No additional fields

class CarDisplay(CarBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    images: Optional[List[str]] = None

# ✅ Ride Schemas
class RideBase(BaseModel):
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    departure_time: datetime
    price_per_seat: float
    total_seats: int
    available_seats: int  # ✅ Kullanılabilir koltuk sayısı eklendi

class RideCreate(RideBase):
    pass  # No additional fields

class RideDisplay(RideBase):
    id: int

    class Config:
        from_attributes = True

class RideUpdate(BaseModel):
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    departure_time: Optional[datetime] = None
    price_per_seat: Optional[float] = None
    total_seats: Optional[int] = None
    available_seats: Optional[int] = None  # ✅ Kullanılabilir koltuk güncelleme desteği

# ✅ Booking Schemas
class BookingBase(BaseModel):
    ride_id: int
    passenger_id: Optional[int]  # Only for online bookings
    phone_number: Optional[str]  # Only for offline bookings
    seats_booked: int

class BookingCreate(BookingBase):
    pass  # No additional fields

class BookingDisplay(BaseModel):
    id: int
    ride_id: int
    passenger_id: Optional[int] = None
    phone_number: Optional[str] = None
    booking_time: datetime
    status: BookingStatus
    seats_booked: int
    refund_amount: Optional[float] = None

    class Config:
        from_attributes = True

class BookingCancel(BaseModel):
    booking_id: int
    cancel_reason: Optional[str] = None  # Cancellation reason (optional)

# ✅ Review Schemas
class ReviewBase(BaseModel):
    ride_id: int
    author_id: int  # User who wrote the review
    target_id: int  # User being reviewed
    review_category: ReviewCategory  # Enum for review type
    star_rating: float = Field(..., ge=1.0, le=5.0, description="Rating must be between 1 and 5")
    review_text: Optional[str] = None
    anonymous_review: bool = False
    media_url: Optional[str] = None  # Image/Video URL

class ReviewCreate(ReviewBase):
    pass  # No additional fields

class ReviewDisplay(ReviewBase):
    id: int
    created_at: datetime
    likes: int
    dislikes: int
    average_rating: float  # Dynamically updated average rating

    class Config:
        from_attributes = True

class ReviewVoteCreate(BaseModel):
    review_id: int
    voter_id: int
    vote_type: ReviewVoteType
  # Enum: Like or Dislike

class ReviewResponseCreate(BaseModel):
    review_id: int
    responder_id: int
    response_text: str

# ✅ Vote Schemas
class ReviewVoteBase(BaseModel):
    review_id: int
    voter_id: int
    vote_type: ReviewVoteType
  # Enum: Like or Dislike

class ReviewVoteDisplay(BaseModel):
    id: int
    vote_type: ReviewVoteType

    created_at: datetime

    class Config:
        from_attributes = True

# ✅ Payment Schemas
class PaymentBase(BaseModel):
    user_id: int
    ride_id: int
    amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod  # ✅ Ödeme yöntemi seçimi için dropdown desteği

class PaymentCreate(PaymentBase):
    pass  # No additional fields

class PaymentRequest(BaseModel):
    user_id: int
    ride_id: int
    amount: float
    payment_method: PaymentMethod  # ✅ Enum (WALLET, CREDIT_CARD, IDEAL, PAYPAL)

class PaymentDisplay(BaseModel):
    id: int
    user_id: int
    ride_id: int
    amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod  # ✅ Enum
    payment_date: datetime

    class Config:
        from_attributes = True

# ✅ Refund Policy Schema
class RefundPolicy(BaseModel):
    refund_percentage_24h: float = 1.0  # 100% refund if canceled 24+ hours before
    refund_percentage_12h: float = 0.5  # 50% refund if canceled 12-24 hours before
    refund_percentage_last_min: float = 0.0  # No refund if canceled less than 12 hours before

# ✅ Authentication Schemas
class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserDisplay

# ✅ User Agreement Schema
class Agreement(BaseModel):
    agreed: bool  # Must be true to proceed with signup
