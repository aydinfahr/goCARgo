from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

### ✅ ENUM DEĞERLERİ (DROP-DOWN İÇİN)
class ReviewType(str, Enum):
    driver = "driver"
    passenger = "passenger"
    car = "car"
    service = "service"

class VoteType(str, Enum):
    like = "like"
    dislike = "dislike"

# ----------------------------------------------------
# ✅ USER SCHEMAS
# ----------------------------------------------------
class UserBase(BaseModel):
    email: str
    username: str
    password: str
    full_name: str

class UserDisplay(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

    class Config:
        from_attributes = True  # Enables ORM conversion

# ----------------------------------------------------
# ✅ CAR SCHEMAS
# ----------------------------------------------------
class CarBase(BaseModel): 
    brand: str 
    model: str
    color: str

class CarDisplay(CarBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# ----------------------------------------------------
# ✅ RIDE SCHEMAS
# ----------------------------------------------------
class RideBase(BaseModel):
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    departure_time: datetime
    price_per_seat: float
    total_seats: int 

class RideDisplay(RideBase):
    id: int

    class Config:
        from_attributes = True

# ----------------------------------------------------
# ✅ BOOKING SCHEMAS
# ----------------------------------------------------
class BookingBase(BaseModel):
    ride_id: int
    passenger_id: int
    seats_booked: int

class BookingDisplay(BookingBase):
    id: int

    class Config:
        from_attributes = True

# ----------------------------------------------------
# ✅ REVIEW SCHEMAS
# ----------------------------------------------------
class ReviewBase(BaseModel):
    ride_id: int
    reviewer_id: int
    reviewee_id: int
    review_type: ReviewType  # ✅ With Enum now it will be a dropdown in Swagger
    rating: float = Field(
        ..., ge=1.0, le=5.0, 
        description="Rating must be a **float** between 1.0 and 5.0 (e.g., **1.0, 2.5, 3.8, 5.0**)"
    )
    comment: Optional[str] = None
    is_anonymous: bool = False # Default: Not anonymous

# 🚀 İncelemelerin Özet Görünümü (User & Ride ile)
class UserSummary(BaseModel):
    id: int
    username: str 

    class Config:
        from_attributes = True

class RideSummary(BaseModel):
    id: int
    start_location: str
    end_location: str

    class Config:
        from_attributes = True

# 🚀 **Review Display - Oylamalar dahil**
class ReviewDisplay(ReviewBase):
    id: int
    review_time: datetime
    media_url: Optional[str] = None
    likes: int
    dislikes: int
    votes: List["ReviewVoteDisplay"] = []  # ✅ Review'e bağlı oyları da göster

    class Config:
        from_attributes = True

# 🚀 **Review Güncelleme Şeması**
class ReviewUpdate(BaseModel):
    ride_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    reviewee_id: Optional[int] = None
    review_type: Optional[ReviewType] = None
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating must be between 1.0 and 5.0")
    comment: Optional[str] = None
    is_anonymous: Optional[bool] = None
    media_url: Optional[str] = None  

# 🚀 **Review Silme Cevap Şeması**
class ReviewDeleteResponse(BaseModel):
    message: str

# ----------------------------------------------------
# ✅ REVIEW VOTE SCHEMAS (LIKE & DISLIKE)
# ----------------------------------------------------
class ReviewVoteBase(BaseModel):
    review_id: int
    user_id: int
    vote_type: VoteType  # ✅ Enum olarak tanımlandı (Dropdown için)

class ReviewVoteDisplay(ReviewVoteBase):
    id: int  # ✅ ID dahil edildi

    class Config:
        from_attributes = True


class ReviewVoteCount(BaseModel):
    likes: int
    dislikes: int


# ----------------------------------------------------
# ✅ REVIEW RESPONSE SCHEMAS 
# ----------------------------------------------------
class ReviewResponseDisplay(BaseModel):
    """
    Schema for displaying review responses.
    """
    id: int
    review_id: int
    responder_id: int
    response_text: str
    response_time: datetime

    class Config:
        from_attributes = True


# ----------------------------------------------------
# ✅ REVIEW DISPLAY SCHEMAS 
# ----------------------------------------------------
class ReviewDisplay(BaseModel):
    id: int
    ride_id: int
    reviewer_id: int
    reviewee_id: int
    review_type: str
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating must be a float between 1.0 and 5.0")
    comment: Optional[str] = None
    is_anonymous: bool = False
    media_url: Optional[str] = None
    review_time: str
    likes: int  # ✅ Shows number of likes
    dislikes: int  # ✅ Shows number of dislikes
   
    # ✅ Added fields for votes and average rating
    vote_count: ReviewVoteCount
    average_rating: float  # ✅ New field added

    # ✅ Response Reviews (Yorumun altındaki cevaplar)
    responses: List[ReviewResponseDisplay] = []
    
    class Config:
        from_attributes = True
        

class ReviewDisplay(ReviewBase):
    id: int
    review_time: datetime
    media_url: Optional[str] = None
    likes: int
    dislikes: int

    responses: List[ReviewResponseDisplay] = []  # ✅ Show responses in the review

    class Config:
        from_attributes = True
