from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    username: str
    password: str
    full_name: str

class UserDisplay(BaseModel):
    username: str
    email: str
    full_name: str
    class Config:
        from_attributes = True  # orm_mode


class CarBase(BaseModel): 
    brand : str 
    model : str
    color : str

class CarDisplay(CarBase): #!!
    owner_id: int
    id: int
    class Config:
        from_attributes = True

    
class RideBase(BaseModel):
    driver_id : int
    car_id : int
    start_location : str
    end_location : str
    departure_time : datetime
    price_per_seat : float
    total_seats : int 

class RideDisplay(RideBase):
    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    ride_id : int
    passenger_id : int
    seats_booked : int

class BookingDisplay(BookingBase):
    pass

class ReviewBase(BaseModel):
    ride_id: int
    reviewer_id: int
    reviewee_id: int
    rating: float
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    review_time: datetime

    class Config:
        orm_mode = True
