from sqlalchemy.orm import Session            
from fastapi import APIRouter, Depends
from db import db_booking
from db.database import get_db
from db.models import DbRide
from schemas import BookingBase, BookingDisplay


router = APIRouter(
    prefix='/booking',
    tags=['booking']
)


# Create booking
@router.post('/', response_model=BookingDisplay)  
def create_booking(request: BookingBase, db: Session=Depends(get_db)):
    return db_booking.create_booking(db, request)

@router.get('/', response_model=BookingDisplay)
def get_booking(id: str, db: Session = Depends(get_db)):  
    return db_booking.get_booking(db, id)