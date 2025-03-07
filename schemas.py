from datetime import datetime
from pydantic import BaseModel, Field


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

class CarDisplay(CarBase): 
    id: int
    class Config:
        from_attributes = True


class RideBase(BaseModel):
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    date: str = Field(..., example=datetime.now().strftime("%d-%m-%Y"))  
    time: str = Field(..., example=datetime.now().strftime("%H:%M"))   
    price_per_seat: float = 1.00
    total_seats: int = 1
    
    class Config:
        from_attributes = True

    def get_departure_datetime(self) -> datetime:
        return datetime.strptime(f"{self.date} {self.time}", "%d-%m-%Y %H:%M")
    

class RideDisplay(BaseModel):
    id: int
    driver_id: int
    car_id: int
    start_location: str
    end_location: str
    departure_time: datetime
    price_per_seat: float
    total_seats: int
    available_seats: int

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    ride_id : int
    passenger_id : int
    seats_booked : int

class BookingDisplay(BookingBase):
    pass

