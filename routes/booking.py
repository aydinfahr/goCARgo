import stripe
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from sqlalchemy.orm import Session
from db import db_payment
from db.database import get_db
from db.models import User, Ride, Booking, Payment
from db.enums import PaymentMethod
from utils.auth import get_current_user, get_current_admin
from utils.notifications import send_notifications
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

# ✅ User books a ride with a selected payment method
@router.post("/book")
def book_ride(
    ride_id: int = Form(...),
    seats_booked: int = Form(...),
    payment_method: PaymentMethod = Form(...),
    token: str = Form(None),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """
    Allows users to book a ride using **Wallet, Credit Card, PayPal, or iDEAL**.
    """
    if seats_booked < 1:
        raise HTTPException(status_code=400, detail="At least one seat must be booked")

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    if seats_booked > ride.available_seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    total_price = ride.price_per_seat * seats_booked

    # ✅ Process the payment
    payment_response = db_payment.make_payment(
        db=db,
        user_id=current_user.id,
        ride_id=ride_id,
        amount=total_price,
        payment_method=payment_method,
        token=token
    )

    if payment_response["status"] != "completed":
        raise HTTPException(status_code=400, detail="Payment failed")

    # ✅ Save the booking
    ride.available_seats -= seats_booked
    booking = Booking(
        ride_id=ride_id,
        passenger_id=current_user.id,
        seats_booked=seats_booked,
        booking_source="online",
        status="confirmed"
    )
    db.add(booking)
    db.commit()

    # ✅ Send notification to the user
    background_tasks.add_task(send_notifications, current_user.phone, current_user.email)

    return {"message": "Booking confirmed", "booking_id": booking.id}

# ✅ Admin creates an offline booking (phone-based)
@router.post("/offline")
def offline_booking(
    ride_id: int = Form(...),
    seats_booked: int = Form(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_admin: User = Depends(get_current_admin)  # ✅ Only admins can use this endpoint
):
    """
    **Admin users** can manually create a booking for users calling by phone.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if seats_booked > ride.available_seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    ride.available_seats -= seats_booked
    booking = Booking(
        ride_id=ride_id,
        seats_booked=seats_booked,
        booking_source="offline",
        status="confirmed"
    )
    db.add(booking)
    db.commit()

    return {"message": "Offline booking confirmed", "booking_id": booking.id}

# ✅ User cancels a booking and receives a refund
@router.post("/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **Cancellation policy:**
    - **More than 24 hours left** → **100% refund**
    - **Between 12-24 hours left** → **50% refund**
    - **Less than 12 hours left** → **No refund**
    """
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.passenger_id == current_user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or unauthorized")
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")

    ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
    payment = db.query(Payment).filter(Payment.ride_id == booking.ride_id, Payment.user_id == current_user.id).first()

    if not ride or not payment:
        raise HTTPException(status_code=404, detail="Ride or payment record not found")

    # ✅ Cancellation & Refund Policy
    time_left = ride.departure_time - datetime.utcnow()
    refund_percentage = 0.0
    if time_left >= timedelta(hours=24):
        refund_percentage = 1.0  # 100% refund
    elif time_left >= timedelta(hours=12):
        refund_percentage = 0.5  # 50% refund

    refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

    # ✅ Process the refund based on payment method
    if payment.payment_method == PaymentMethod.WALLET.value:
        current_user.wallet_balance += refund_amount
    elif payment.payment_method == PaymentMethod.CREDIT_CARD.value:
        db_payment.refund_payment(db, payment.id)

    booking.status = "cancelled"
    booking.refund_amount = refund_amount
    db.commit()

    return {"message": "Booking cancelled", "refund": refund_amount}

# ✅ Retrieve all bookings of a user
@router.get("/{user_id}")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all bookings made by a user.
    """
    bookings = db.query(Booking).filter(Booking.passenger_id == user_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user")
    return bookings

# ✅ Admin: Retrieve all bookings in the system
@router.get("/admin/all")
def get_all_bookings(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """
    Retrieve all bookings in the system for **Admin Users**.
    """
    return db.query(Booking).all()

# ✅ Admin: Retrieve bookings for a specific ride
@router.get("/ride/{ride_id}")
def get_bookings_for_ride(ride_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all bookings for a specific ride for **Admin Users**.
    """
    bookings = db.query(Booking).filter(Booking.ride_id == ride_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this ride")
    return bookings
