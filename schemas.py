from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ✅ Kullanıcı Rolleri (Dropdown Seçimi İçin)
class UserRole(str, Enum):
    driver = "driver"
    passenger = "passenger"
    admin = "admin"

# ✅ Kullanıcı Kayıt Şeması (Form Kullanımı İçin)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole  # 🚀 Dropdown olarak ayarlanacak
    agreed_terms: bool  # 🚀 Checkbox (True/False)


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
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole  # 🚀 Dropdown olarak ayarlanacak

class UserCreate(UserBase):
    agreed_terms: bool  # Kullanıcı sözleşmesini kabul etmeli


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


# ✅ Araç Şemaları
class CarBase(BaseModel):
    brand: str
    model: str
    color: str
    images: Optional[List[str]] = None  # Car images


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


# ✅ Yolculuk Şemaları
class RideBase(BaseModel):
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    departure_time: datetime
    price_per_seat: float
    total_seats: int


class RideCreate(RideBase):
    pass


class RideDisplay(RideBase):
    id: int
    available_seats: int

    class Config:
        from_attributes = True


class RideUpdate(BaseModel):
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    departure_time: Optional[datetime] = None
    price_per_seat: Optional[float] = None
    total_seats: Optional[int] = None


# ✅ Rezervasyon Şemaları
class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


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
    cancel_reason: Optional[str] = None  # İptal nedeni (isteğe bağlı)


# ✅ Yorum Şemaları
class ReviewCategory(str, Enum):
    DRIVER = "driver"
    PASSENGER = "passenger"
    CAR = "car"
    SERVICE = "service"


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
    pass


class ReviewDisplay(ReviewBase):
    id: int
    created_at: datetime
    likes: int
    dislikes: int
    average_rating: float  # ✅ Real-time updated average rating

    class Config:
        from_attributes = True


class ReviewVoteCreate(BaseModel):
    review_id: int
    voter_id: int
    vote_type: str  # Örneğin: "like" veya "dislike"


class ReviewResponseCreate(BaseModel):
    review_id: int
    responder_id: int
    response_text: str


# ✅ Oylama Şemaları
class VoteType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"


class ReviewVoteBase(BaseModel):
    review_id: int
    voter_id: int
    vote_type: VoteType  # Enum: Like or Dislike


class ReviewVoteDisplay(BaseModel):
    id: int
    vote_type: VoteType
    created_at: datetime

    class Config:
        from_attributes = True


# ✅ Ödeme Şemaları
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentBase(BaseModel):
    user_id: int
    ride_id: int
    amount: float
    payment_status: PaymentStatus


class PaymentCreate(PaymentBase):
    pass


class PaymentDisplay(BaseModel):
    id: int
    user_id: int
    ride_id: int
    amount: float
    payment_status: PaymentStatus
    payment_date: datetime

    class Config:
        from_attributes = True


# ✅ Geri Ödeme Şeması
class RefundPolicy(BaseModel):
    refund_percentage_24h: float = 1.0  # 100% refund if cancelled 24+ hours before
    refund_percentage_12h: float = 0.5  # 50% refund if cancelled 12-24 hours before
    refund_percentage_last_min: float = 0.0  # No refund if cancelled less than 12 hours


# ✅ Kimlik Doğrulama Şemaları
class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserDisplay


# ✅ Kullanıcı Sözleşmesi Şeması
class Agreement(BaseModel):
    agreed: bool  # Must be true to proceed with signup
