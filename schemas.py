from pydantic import BaseModel, EmailStr, Field
from fastapi import UploadFile, Form, File
from typing import Optional, List
from enum import Enum
from datetime import datetime
from db.enums import (
    UserRole,  # ✅ ENUM Import to avoid conflicts
    ReviewCategory,
    ReviewVoteType,
    PaymentStatus,
    PaymentMethod,
    BookingStatus,
    ComplaintStatus
)

# ================================
# ✅ User Schemas
# ================================

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
    profile_picture: Optional[str] = None

    class Config:
        use_enum_values = True  # Ensures FastAPI returns ENUM as a string
        from_attributes = True  # Enables ORM mode

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    current_username: str  # Required to prevent accidental changes
    new_username: Optional[str] = None
    current_email: EmailStr  # Required to verify identity
    new_email: Optional[EmailStr] = None
    new_full_name: Optional[str] = None
    profile_picture: Optional[str] = None  # Changed from UploadFile

    class Config:
        from_attributes = True

class UserDeleteResponse(BaseModel):
    message: str

# ================================
# ✅ Authentication Schemas
# ================================

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserDisplay

class TokenData(BaseModel):
    user_id: int
    email: Optional[EmailStr] = None  # Added for better authentication flow

# ================================
# ✅ Car Schemas
# ================================

class CarBase(BaseModel):
    brand: str
    model: str
    color: str
    images: Optional[List[str]] = None  # List of car image URLs

class CarCreate(CarBase):
    pass

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

# ================================
# ✅ Ride Schemas
# ================================

class RideBase(BaseModel):
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    departure_time: datetime
    price_per_seat: float
    total_seats: int
    available_seats: int  # Added available seats field

class RideCreate(RideBase):
    pass

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
    available_seats: Optional[int] = None  # Added support for updating available seats

# ================================
# ✅ Booking Schemas
# ================================

class BookingBase(BaseModel):
    ride_id: int
    passenger_id: Optional[int]  # Only for online bookings
    phone_number: Optional[str]  # Only for offline bookings
    seats_booked: int

class BookingCreate(BookingBase):
    pass

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

# ================================
# ✅ Payment Schemas
# ================================

class PaymentCreate(BaseModel):
    user_id: int
    ride_id: int
    amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod

class PaymentRequest(BaseModel):
    user_id: int
    ride_id: int
    amount: float
    payment_method: PaymentMethod  # ENUM: WALLET, CREDIT_CARD, IDEAL, PAYPAL

class PaymentDisplay(BaseModel):
    id: int
    user_id: int
    ride_id: int
    amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    payment_date: datetime

    class Config:
        from_attributes = True  # Enables ORM mode

# ================================
# ✅ Review Schemas
# ================================

class ReviewBase(BaseModel):
    ride_id: int
    author_id: int  # User who wrote the review
    target_id: int  # User being reviewed
    review_category: ReviewCategory  # Enum for review type
    star_rating: float = Field(..., ge=1.0, le=5.0, description="Rating must be between 1 and 5")
    review_text: Optional[str] = None
    anonymous_review: bool = False
    media_url: Optional[str] = None  # Image/Video URL

class ReviewCreate(BaseModel):
    ride_id: int = Form(...)
    reviewer_id: int = Form(...)
    reviewee_id: int = Form(...)
    review_category: ReviewCategory = Form(...)  # ✅ Dropdown olarak gelecek
    star_rating: float = Form(..., ge=1.0, le=5.0)
    review_text: Optional[str] = Form(None)
    anonymous_review: bool = Form(False)
    media_file: Optional[UploadFile] = File(None)

    class Config:
        from_attributes = True

class ReviewDisplay(ReviewBase):
    id: int
    created_at: datetime
    likes: int
    dislikes: int
    average_rating: float  # Dynamically updated average rating

    class Config:
        from_attributes = True

class ReviewCategory(str, Enum):
    ABOUT_DRIVER = "about_driver"
    ABOUT_PASSENGER = "about_passenger"
    ABOUT_CAR = "about_car"
    ABOUT_SERVICE = "about_service"

class ReviewVoteCreate(BaseModel):
    review_id: int
    voter_id: int
    vote_type: ReviewVoteType  # Enum: Like or Dislike

class ReviewResponseCreate(BaseModel):
    review_id: int
    responder_id: int
    response_text: str

# ================================
# ✅ User Agreement Schema
# ================================

class Agreement(BaseModel):
    agreed: bool  # Must be true to proceed with signup