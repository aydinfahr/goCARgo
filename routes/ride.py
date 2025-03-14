from enum import Enum
from typing import Optional
from sqlalchemy.orm import Session            
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from db import db_ride
from db.database import get_db
from db.enums import NumberOfSeats, RideStatus
from db.models import User
from schemas import RideBase, RideDisplay
from utils.auth import get_current_user


router = APIRouter(
    prefix='/rides',
    tags=['Ride']
)

# Create a ride
@router.post('/', response_model=RideDisplay)  
def create_ride(request: RideBase, db: Session=Depends(get_db)):
    return db_ride.create_ride(db, request)
  
# # List user's rides
# @router.get("/", response_model=list[RideDisplay])
# def get_all_rides(
#     db: Session = Depends(get_db), 
#     driver_id: Optional[int] = None,
#     status: Optional[RideStatus] = None 
# ):
#     return db_ride.get_all_rides(db, driver_id, status)


# Search rides with filter
@router.get('/', response_model=list[RideDisplay])
def search_rides(
    driver_id: Optional[int] = None,
    status: Optional[RideStatus] = None,
    start_location : Optional[str] = None,
    end_location : Optional[str] = None,
    departure_date : Optional[date] = None, 
    number_of_seats : Optional[NumberOfSeats] = None,
    db: Session=Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """Search rides with filter, if no filter is provided, return all rides with admin privileges"""
    if not current_user.is_admin:
        if driver_id:
            if driver_id != current_user.id:
                raise HTTPException(status_code=403, detail="Unauthorized users cannot filter by driver_id")
            if status != RideStatus.upcoming:
                raise HTTPException(status_code=403, detail="Unauthorized users can only see upcoming rides")
            
 
    return db_ride.search_rides(
        db,
        driver_id,
        status,
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
def update_ride(id: int, request: RideBase, db: Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.id != request.driver_id:
            raise HTTPException(status_code=403, detail="You are not authorized to update this ride")
    return db_ride.update_ride(db, id, request)

# Delete ride
@router.delete("/{id}", response_model=RideDisplay)
def delete_ride(driver_id: int, id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.id != driver_id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this ride")
    return db_ride.delete_ride(db, driver_id, id)

