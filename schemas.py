from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


### ✅ USER SCHEMAS
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


### ✅ CAR SCHEMAS
class CarBase(BaseModel): 
    brand: str 
    model: str
    color: str


class CarDisplay(CarBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


### ✅ RIDE SCHEMAS
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


### ✅ BOOKING SCHEMAS
class BookingBase(BaseModel):
    ride_id: int
    passenger_id: int
    seats_booked: int


class BookingDisplay(BookingBase):
    id: int  # Ensure the display schema includes an ID

    class Config:
        from_attributes = True


### ✅ REVIEW SCHEMAS
# Base Review Schema for Creating a Review
class ReviewBase(BaseModel):
    ride_id: int
    user_id: int
    reviewer_id: int
    reviewee_id: int
    rating: float = Field(..., ge=0, le=5, description="Rating must be between 0 and 5")
    comment: Optional[str] = None


# Summary Schema for User Response
class UserSummary(BaseModel):
    id: int
    username: str  # Changed from `name` to `username` for consistency

    class Config:
        from_attributes = True


# Summary Schema for Ride Response
class RideSummary(BaseModel):
    id: int
    start_location: str
    end_location: str

    class Config:
        from_attributes = True


# Review Response Schema with Linked User and Ride Data
class ReviewDisplay(ReviewBase):
    id: int
    review_time: datetime
    user: Optional[UserSummary] = None  # The user who received the review
    reviewer: Optional[UserSummary] = None  # The user who wrote the review
    reviwee: Optional[UserSummary] = None  # The user associated with the review
    ride: Optional[RideSummary] = None  # The ride associated with the review

    class Config:
        from_attributes = True


# Schema for Updating a Review (All Fields Optional)
class ReviewUpdate(BaseModel):
    ride_id: Optional[int] = None
    user_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    reviwee_id: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=5, description="Rating must be between 0 and 5")
    comment: Optional[str] = None


# Schema for DELETE Response
class ReviewDeleteResponse(BaseModel):
    message: str
