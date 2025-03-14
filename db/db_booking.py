from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Booking, Ride, User, Payment
from schemas import BookingBase
from datetime import datetime, timedelta
from fastapi import HTTPException

def create_booking(db: Session, request: BookingBase):
    user = db.query(User).filter(User.id == request.passenger_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    #  if not user.verified_email:
    #     raise HTTPException(status_code=400, detail="You must verify your email before booking.")

    ride = db.query(Ride).filter(Ride.id == request.ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if request.passenger_id == ride.driver_id:
        raise HTTPException(status_code=400, detail="You cannot book your own ride.")

    existing_booking = db.query(Booking).filter(
        Booking.ride_id == request.ride_id,
        Booking.passenger_id == request.passenger_id
    ).first()
    if existing_booking:
        raise HTTPException(status_code=400, detail="You have already booked this ride.")

    if request.seats_booked <= 0:
        raise HTTPException(status_code=400, detail="Invalid seat count. Must be at least 1.")

    if ride.available_seats < request.seats_booked:
        raise HTTPException(status_code=400, detail="Not enough available seats.")
    
    new_booking = Booking(
        ride_id=request.ride_id,
        passenger_id=request.passenger_id,
        seats_booked=request.seats_booked,

        status="confirmed" if ride.instant_booking else "pending"
    )
    try:
        db.add(new_booking)
        ride.available_seats -= request.seats_booked
        db.commit()
        db.refresh(new_booking)

        # 🚀 Eğer Instant Booking açıksa kullanıcıya onay e-postası gönder
        # if ride.instant_booking:
        #     send_email(user.email, "Your booking is confirmed!", f"Your booking for ride {ride.id} has been confirmed.")
        # else:
        #     # 🚀 Eğer Instant Booking kapalıysa, sürücüye onay e-postası gönder
        #     driver = db.query(DbUser).filter(DbUser.id == ride.driver_id).first()
        #     send_email(driver.email, "New Booking Request", f"You have a new booking request for ride {ride.id}. Please confirm or reject it.")

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database error: Possible duplicate booking.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    return new_booking


# def get_all_bookings(db: Session, passenger_id: int, ride_id: int):
#     booking_query =  db.query(Booking)

#     if passenger_id:
#         booking_query = booking_query.filter(Booking.passenger_id == passenger_id)

#     if ride_id:
#         booking_query = booking_query.filter(Booking.ride_id == ride_id)
#     bookings = booking_query.all()

#     return bookings


def update_booking(db: Session, booking_id: int, request: BookingBase) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Booking is not in a pending state.")

    if request.seats_booked <= 0:
        raise HTTPException(status_code=400, detail="Invalid seat count. Must be at least 1.")

    if ride.available_seats + booking.seats_booked < request.seats_booked:
        raise HTTPException(status_code=400, detail="Not enough available seats.")

    ride.available_seats += booking.seats_booked
    booking.seats_booked = request.seats_booked
    ride.available_seats -= request.seats_booked

    db.commit()
    db.refresh(booking)

    return booking



def update_booking_status(db: Session, booking_id: int, status: str) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
 
    if booking.status != "pending":
        raise HTTPException(status_code=400, detail="Booking is not in a pending state.")

    booking.status = status

    if status == "rejected":
        ride.available_seats += booking.seats_booked

    db.commit()
    db.refresh(booking)

    return booking  




