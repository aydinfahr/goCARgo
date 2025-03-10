from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Booking, Ride, User, Payment
from schemas import BookingCreate, BookingCancel
from datetime import datetime, timedelta
from fastapi import HTTPException

def create_booking(db: Session, booking_data: BookingCreate):
    """
    Creates a new booking for a ride.

    Args:
        db (Session): The database session.
        booking_data (BookingCreate): Booking creation schema.

    Returns:
        Booking: The created booking object.
    """
    ride = db.query(Ride).filter(Ride.id == booking_data.ride_id).first()
    passenger = db.query(User).filter(User.id == booking_data.passenger_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")

    if booking_data.seats_booked > ride.total_seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    total_price = ride.price_per_seat * booking_data.seats_booked

    if passenger.wallet_balance < total_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Deduct payment from user's wallet
    passenger.wallet_balance -= total_price
    ride.total_seats -= booking_data.seats_booked

    # Create booking entry
    new_booking = Booking(
        ride_id=booking_data.ride_id,
        passenger_id=booking_data.passenger_id,
        seats_booked=booking_data.seats_booked,
        booking_source="online",
        status="confirmed"
    )

    # Create payment entry
    new_payment = Payment(
        user_id=booking_data.passenger_id,
        ride_id=booking_data.ride_id,
        amount=total_price,
        payment_status="completed"
    )

    db.add(new_booking)
    db.add(new_payment)

    try:
        db.commit()
        db.refresh(new_booking)
        return new_booking
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Booking could not be created due to database constraints.")

def get_booking_by_id(db: Session, booking_id: int):
    """
    Fetches a booking by its ID.

    Args:
        db (Session): The database session.
        booking_id (int): The ID of the booking.

    Returns:
        Booking: The retrieved booking object.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking

def get_bookings_for_user(db: Session, user_id: int):
    """
    Retrieves all bookings made by a specific user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[Booking]: List of bookings for the user.
    """
    bookings = db.query(Booking).filter(Booking.passenger_id == user_id).all()

    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user.")

    return bookings

def cancel_booking(db: Session, booking_id: int):
    """
    Cancels a booking and processes a refund.

    Args:
        db (Session): The database session.
        booking_id (int): The ID of the booking.

    Returns:
        dict: Confirmation message and refund details.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
    passenger = db.query(User).filter(User.id == booking.passenger_id).first()

    if not ride or not passenger:
        raise HTTPException(status_code=404, detail="Ride or passenger not found")

    # Refund calculation
    time_left = ride.departure_time - datetime.utcnow()
    refund_percentage = 0.0

    if time_left >= timedelta(hours=24):
        refund_percentage = 1.0  # 100% refund
    elif time_left >= timedelta(hours=12):
        refund_percentage = 0.5  # 50% refund

    refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

    # Process refund
    passenger.wallet_balance += refund_amount
    booking.status = "cancelled"
    booking.refund_amount = refund_amount

    db.commit()

    return {"message": "Booking cancelled", "refund": refund_amount}

def get_bookings_for_ride(db: Session, ride_id: int):
    """
    Retrieves all bookings for a specific ride.

    Args:
        db (Session): The database session.
        ride_id (int): The ID of the ride.

    Returns:
        List[Booking]: List of bookings for the ride.
    """
    bookings = db.query(Booking).filter(Booking.ride_id == ride_id).all()

    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this ride")

    return bookings

def delete_booking(db: Session, booking_id: int):
    """
    Deletes a booking from the database.

    Args:
        db (Session): The database session.
        booking_id (int): The ID of the booking to be deleted.

    Returns:
        dict: Confirmation message.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    db.delete(booking)
    db.commit()

    return {"message": "Booking deleted successfully"}
