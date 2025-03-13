from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from db.enums import (
    ReviewCategory,
    ReviewVoteType,
    PaymentStatus,
    PaymentMethod,
    BookingStatus,
    ComplaintStatus
)

# ✅ User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    agreed_terms: bool = Field(..., description="User must accept terms and conditions")

    @classmethod
    def validate_agreed_terms(cls, v):
        if v is False:
            raise ValueError("❌ You must accept the terms and conditions to register.")
        return v

class UserDisplay(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    is_admin: bool
    is_banned: bool
    rating: float
    rating_count: int
    verified_id: bool
    verified_email: bool
    agreed_terms: bool
    member_since: datetime

    class Config:
        from_attributes = True  # ✅ Enable ORM mode for SQLAlchemy


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str
    full_name: Optional[str] = None
    # profile_picture: Optional[str] = None

class UserDeleteResponse(BaseModel):
    message: str

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# ✅ Car Schemas
class CarBase(BaseModel): 
    owner_id: int
    brand: str 
    model: str
    color: str

class CarDisplay(CarBase): 
    id: int

    class Config:
        from_attributes = True

# ✅ Ride Schemas
from pydantic import BaseModel, Field
from datetime import datetime

# ✅ Ride Schemas
class RideBase(BaseModel):
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    departure_time: datetime  # ✅ datetime type used instead of date+time
    price_per_seat: float = Field(..., gt=0, description="Price per seat must be greater than zero.")
    total_seats: int = Field(..., ge=1, le=4, description="Total seats must be between 1 and 4.")
    instant_booking: bool = False  # ✅ Ensuring it's a valid boolean

    class Config:
        from_attributes = True

# ✅ Display Ride Data
class RideDisplay(RideBase):
    id: int
    available_seats: int

    class Config:
        from_attributes = True


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
    reviewer_id: int  # User who wrote the review
    reviewee_id: int  # User being reviewed
    review_category: ReviewCategory  # Enum for review type
    star_rating: float = Field(..., ge=1.0, le=5.0, description="Rating must be between 1 and 5")
    review_text: Optional[str] = None
    anonymous_review: bool = False
    media_url: Optional[str] = None  # Image/Video URL
    created_at: Optional[datetime] = None

class ReviewCreate(ReviewBase):
    created_at: datetime = Field(default_factory=datetime.utcnow) 

class ReviewDisplay(ReviewBase):
    id: int
    created_at: datetime
    likes: Optional[int] = 0 
    dislikes: Optional[int] = 0
    average_rating: Optional[float] = 0.0  # Dynamically updated average rating

    class Config:
        from_attributes = True

class ReviewVoteCreate(BaseModel):
    review_id: int
    voter_id: int
    vote_type: ReviewVoteType  # Enum: Like or Dislike

class ReviewResponseCreate(BaseModel):
    review_id: int
    responder_id: int
    response_text: str

# ✅ Vote Schemas
class ReviewVoteBase(BaseModel):
    review_id: int
    voter_id: int
    vote_type: ReviewVoteType  # Enum: Like or Dislike

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
    payment_method: PaymentMethod  

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
