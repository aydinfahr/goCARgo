from datetime import datetime
from pydantic import BaseModel


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
    owner_id : int
    brand : str 
    model : str
    color : str

class CarDisplay(CarBase): #!!
    id: int

    
class RideBase(BaseModel):
    driver_id : int
    car_id : int
    start_location : str
    end_location : str
    departure_time : datetime
    price_per_seat : float
    available_seats : int 

class RideDisplay(RideBase):
    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    id :int
    ride_id : int
    passenger_id : int
    seats_booked : int

class BookingDisplay(BookingBase):
    pass
