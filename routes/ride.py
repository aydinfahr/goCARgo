from enum import Enum
from typing import Optional
from sqlalchemy.orm import Session            
from fastapi import APIRouter, Depends
from datetime import date
from db import db_ride
from db.database import get_db
from enums import NumberOfSeats, RideStatus
from schemas import RideBase, RideDisplay


router = APIRouter(
    prefix='/ride',
    tags=['ride']
)

# Create a ride
@router.post('/', response_model=RideDisplay)  
def create_ride(request: RideBase, db: Session=Depends(get_db)):
    return db_ride.create_ride(db, request)
  
# List user's rides
@router.get("/", response_model=list[RideDisplay])
def get_all_rides(
    db: Session = Depends(get_db), 
    driver_id: Optional[int] = None,
    status: Optional[RideStatus] = None 
):
    return db_ride.get_all_rides(db, driver_id, status)


# Search rides with filter
@router.get('/search', response_model=list[RideDisplay])
def search_rides(
    start_location : Optional[str] = None,
    end_location : Optional[str] = None,
    departure_date : Optional[date] = date.today(), 
    number_of_seats : Optional[NumberOfSeats] = None,
    db: Session=Depends(get_db)
    ):
    return db_ride.search_rides(
        db,
        start_location,
        end_location,
        departure_date, 
        number_of_seats.value if number_of_seats else None
        ) 

# Get ride details
@router.get('/{id}', response_model=RideDisplay)
def get_ride(id: int, db: Session = Depends(get_db)): 
    return  db_ride.get_ride(db, id)

# Update ride details
@router.put('/{id}', response_model=RideDisplay)
def update_ride(id: int, request: RideBase, db: Session=Depends(get_db)):
    return db_ride.update_ride(db, id, request)

# Delete ride
@router.delete("/{id}", response_model=RideDisplay)
def delete_ride(driver_id: int, id: int, db: Session = Depends(get_db)):
    return db_ride.delete_ride(db, driver_id, id)

