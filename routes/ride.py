from typing import Optional
from sqlalchemy.orm import Session            
from fastapi import APIRouter, Depends
from datetime import date
from db import db_ride
from db.database import get_db
from schemas import RideBase, RideDisplay


router = APIRouter(
    prefix='/ride',
    tags=['ride']
)


# Create ride
@router.post('/', response_model=RideDisplay)  
def create_ride(request: RideBase, db: Session=Depends(get_db)):
    return db_ride.create_ride(db, request)
    



@router.get('/', response_model=RideDisplay)
def get_ride(id: str, db: Session = Depends(get_db)): 
    return db_ride.get_ride(db, id)



# Search rides with filter
@router.get('/search', response_model=list[RideDisplay])
def search_rides(
    start_location : Optional[str] = None,
    end_location : Optional[str] = None,
    departure_date : Optional[date] = None, 
    number_of_seats : Optional[int] = None,
    db: Session=Depends(get_db)
    ):
    return db_ride.search_ride(
        db,
        start_location,
        end_location,
        departure_date, 
        number_of_seats,
        )



