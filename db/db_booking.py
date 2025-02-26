from sqlalchemy.orm.session import Session
from schemas import BookingBase
from db.models import DbBooking

def create_booking(db: Session, request: BookingBase):
    new_booking = DbBooking(
        id = request.id,
        ride_id = request.ride_id,
        passenger_id = request.passenger_id,
        seats_booked = request.seats_booked

    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

def get_booking(db: Session, id:int):
    #handle any exception
    return db.query(DbBooking).filter(DbBooking.id == id).first()