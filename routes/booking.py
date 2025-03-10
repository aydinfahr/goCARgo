# # # from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
# # # from sqlalchemy.orm import Session
# # # from db import db_booking
# # # from schemas import BookingCreate, BookingDisplay
# # # from db.database import get_db
# # # from db.models import User, Ride, Booking, Payment
# # # from utils.notifications import send_notifications, send_sms  # ✅ SMS & Email gönderme fonksiyonlarını ekle
# # # from datetime import datetime, timedelta



# # # router = APIRouter(
# # #     prefix="/bookings",
# # #     tags=["Bookings"]
# # # )

# # # # ✅ Book a ride (Online)
# # # @router.post("/book")
# # # def book_ride(
# # #     ride_id: int,
# # #     passenger_id: int,
# # #     seats_booked: int,
# # #     background_tasks: BackgroundTasks,  # ✅ Arka planda bildirim göndermek için ekle
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """
# # #     Allows users to book a ride online.
# # #     """
# # #     ride = db.query(Ride).filter(Ride.id == ride_id).first()
# # #     passenger = db.query(User).filter(User.id == passenger_id).first()

# # #     if not ride:
# # #         raise HTTPException(status_code=404, detail="Ride not found")

# # #     if not passenger:
# # #         raise HTTPException(status_code=404, detail="Passenger not found")

# # #     if seats_booked > ride.total_seats:
# # #         raise HTTPException(status_code=400, detail="Not enough seats available")

# # #     total_price = ride.price_per_seat * seats_booked

# # #     if passenger.wallet_balance < total_price:
# # #         raise HTTPException(status_code=400, detail="Insufficient balance")

# # #     # Deduct payment from user wallet
# # #     passenger.wallet_balance -= total_price
# # #     ride.total_seats -= seats_booked

# # #     # Create booking
# # #     booking = Booking(
# # #         ride_id=ride_id,
# # #         passenger_id=passenger_id,
# # #         seats_booked=seats_booked,
# # #         booking_source="online",
# # #         status="confirmed"
# # #     )

# # #     # Create payment entry
# # #     payment = Payment(
# # #         user_id=passenger_id,
# # #         ride_id=ride_id,
# # #         amount=total_price,
# # #         payment_status="completed"
# # #     )

# # #     db.add(booking)
# # #     db.add(payment)
# # #     db.commit()

# # #     # ✅ Arka planda SMS ve E-posta bildirimi gönder
# # #     background_tasks.add_task(send_notifications, passenger.phone, passenger.email)

# # #     return {"message": "Booking confirmed", "booking_id": booking.id}


# # # # ✅ Offline Booking (Admin only)
# # # @router.post("/offline")
# # # def offline_booking(
# # #     ride_id: int,
# # #     phone_number: str,
# # #     seats_booked: int,
# # #     background_tasks: BackgroundTasks,  # ✅ Arka planda bildirim göndermek için ekle
# # #     db: Session = Depends(get_db)
# # # ):
# # #     """
# # #     Allows an admin to book a ride for a user who calls in.
# # #     """
# # #     ride = db.query(Ride).filter(Ride.id == ride_id).first()

# # #     if not ride:
# # #         raise HTTPException(status_code=404, detail="Ride not found")

# # #     if seats_booked > ride.total_seats:
# # #         raise HTTPException(status_code=400, detail="Not enough seats available")

# # #     ride.total_seats -= seats_booked

# # #     booking = Booking(
# # #         ride_id=ride_id,
# # #         phone_number=phone_number,
# # #         seats_booked=seats_booked,
# # #         booking_source="offline",
# # #         status="confirmed"
# # #     )

# # #     db.add(booking)
# # #     db.commit()

# # #     # ✅ Arka planda SMS bildirimi gönder (çünkü telefon numarası var, e-posta olmayabilir)
# # #     background_tasks.add_task(send_notifications, phone_number, None)

# # #     return {"message": "Offline booking confirmed", "booking_id": booking.id}


# # # # ✅ Cancel Booking with Refund
# # # @router.post("/{booking_id}/cancel")
# # # def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
# # #     """
# # #     Cancels a booking and provides a refund based on cancellation time.
# # #     """
# # #     booking = db.query(Booking).filter(Booking.id == booking_id).first()

# # #     if not booking:
# # #         raise HTTPException(status_code=404, detail="Booking not found")

# # #     if booking.status == "cancelled":
# # #         raise HTTPException(status_code=400, detail="Booking is already cancelled")

# # #     ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
# # #     passenger = db.query(User).filter(User.id == booking.passenger_id).first()

# # #     if not ride or not passenger:
# # #         raise HTTPException(status_code=404, detail="Ride or passenger not found")

# # #     # Refund calculation
# # #     time_left = ride.departure_time - datetime.utcnow()
# # #     refund_percentage = 0.0

# # #     if time_left >= timedelta(hours=24):
# # #         refund_percentage = 1.0  # 100% refund
# # #     elif time_left >= timedelta(hours=12):
# # #         refund_percentage = 0.5  # 50% refund

# # #     refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

# # #     # Process refund
# # #     passenger.wallet_balance += refund_amount
# # #     booking.status = "cancelled"
# # #     booking.refund_amount = refund_amount

# # #     db.commit()

# # #     return {"message": "Booking cancelled", "refund": refund_amount}


# # # # ✅ Get User's Bookings
# # # @router.get("/{user_id}")
# # # def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
# # #     """
# # #     Retrieves all bookings made by a specific user.
# # #     """
# # #     bookings = db.query(Booking).filter(Booking.passenger_id == user_id).all()

# # #     if not bookings:
# # #         raise HTTPException(status_code=404, detail="No bookings found for this user")

# # #     return bookings


# # # # ✅ Admin: Get All Bookings
# # # @router.get("/admin/all")
# # # def get_all_bookings(db: Session = Depends(get_db)):
# # #     """
# # #     Retrieves all bookings in the system (Admin only).
# # #     """
# # #     bookings = db.query(Booking).all()
# # #     return bookings


# # # # ✅ Admin: Get Bookings for a Ride
# # # @router.get("/ride/{ride_id}")
# # # def get_bookings_for_ride(ride_id: int, db: Session = Depends(get_db)):
# # #     """
# # #     Retrieves all bookings for a specific ride (Admin only).
# # #     """
# # #     bookings = db.query(Booking).filter(Booking.ride_id == ride_id).all()

# # #     if not bookings:
# # #         raise HTTPException(status_code=404, detail="No bookings found for this ride")

# # #     return bookings


# # from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
# # from sqlalchemy.orm import Session
# # from db import db_booking, db_payment
# # from schemas import BookingCreate, BookingDisplay
# # from db.database import get_db
# # from db.models import User, Ride, Booking, Payment
# # from utils.notifications import send_notifications, send_sms
# # from datetime import datetime, timedelta
# # from routes.payment import make_payment  # ✅ Ödeme işlemini çağırmak için içe aktar

# # router = APIRouter(
# #     prefix="/bookings",
# #     tags=["Bookings"]
# # )

# # # ✅ Kullanıcı Ödeme Seçerek Yolculuk Rezervasyonu Yapmalı
# # @router.post("/book")
# # def book_ride(
# #     ride_id: int = Form(...),
# #     passenger_id: int = Form(...),
# #     seats_booked: int = Form(...),
# #     payment_method: str = Form(...),  # ✅ Dropdown
# #     token: str = Form(None),  # ✅ Kredi Kartı için
# #     background_tasks: BackgroundTasks = Depends(),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Allows users to book a ride online using Wallet, Credit Card, PayPal, or iDEAL.
# #     """
# #     ride = db.query(Ride).filter(Ride.id == ride_id).first()
# #     passenger = db.query(User).filter(User.id == passenger_id).first()

# #     if not ride:
# #         raise HTTPException(status_code=404, detail="Ride not found")
# #     if not passenger:
# #         raise HTTPException(status_code=404, detail="Passenger not found")
# #     if seats_booked > ride.total_seats:
# #         raise HTTPException(status_code=400, detail="Not enough seats available")

# #     total_price = ride.price_per_seat * seats_booked

# #     # ✅ Ödeme işlemi çağır
# #     payment_response = make_payment(
# #         ride_id=ride_id,
# #         amount=total_price,
# #         payment_method=payment_method,
# #         token=token,
# #         db=db,
# #         current_user=passenger
# #     )

# #     if payment_response["status"] != "completed":
# #         raise HTTPException(status_code=400, detail="Payment failed")

# #     # ✅ Rezervasyonu kaydet
# #     ride.total_seats -= seats_booked
# #     booking = Booking(
# #         ride_id=ride_id,
# #         passenger_id=passenger_id,
# #         seats_booked=seats_booked,
# #         booking_source="online",
# #         status="confirmed"
# #     )
# #     db.add(booking)
# #     db.commit()

# #     # ✅ Arka planda SMS & E-posta bildirimi gönder
# #     background_tasks.add_task(send_notifications, passenger.phone, passenger.email)

# #     return {"message": "Booking confirmed", "booking_id": booking.id}

# # # ✅ Offline Booking (Admin only)
# # @router.post("/offline")
# # def offline_booking(
# #     ride_id: int = Form(...),
# #     phone_number: str = Form(...),
# #     seats_booked: int = Form(...),
# #     background_tasks: BackgroundTasks = Depends(),
# #     db: Session = Depends(get_db)
# # ):
# #     """
# #     Allows an admin to book a ride for a user who calls in.
# #     """
# #     ride = db.query(Ride).filter(Ride.id == ride_id).first()

# #     if not ride:
# #         raise HTTPException(status_code=404, detail="Ride not found")

# #     if seats_booked > ride.total_seats:
# #         raise HTTPException(status_code=400, detail="Not enough seats available")

# #     ride.total_seats -= seats_booked
# #     booking = Booking(
# #         ride_id=ride_id,
# #         phone_number=phone_number,
# #         seats_booked=seats_booked,
# #         booking_source="offline",
# #         status="confirmed"
# #     )
# #     db.add(booking)
# #     db.commit()

# #     # ✅ SMS bildirimi gönder
# #     background_tasks.add_task(send_notifications, phone_number, None)

# #     return {"message": "Offline booking confirmed", "booking_id": booking.id}

# # # ✅ İptal ve Para İadesi (Ödeme Yöntemine Göre)
# # @router.post("/{booking_id}/cancel")
# # def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
# #     """
# #     Cancels a booking and provides a refund based on cancellation time & payment method.
# #     """
# #     booking = db.query(Booking).filter(Booking.id == booking_id).first()
# #     if not booking:
# #         raise HTTPException(status_code=404, detail="Booking not found")
# #     if booking.status == "cancelled":
# #         raise HTTPException(status_code=400, detail="Booking is already cancelled")

# #     ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
# #     passenger = db.query(User).filter(User.id == booking.passenger_id).first()
# #     payment = db.query(Payment).filter(Payment.ride_id == booking.ride_id, Payment.user_id == booking.passenger_id).first()

# #     if not ride or not passenger or not payment:
# #         raise HTTPException(status_code=404, detail="Ride, passenger, or payment record not found")

# #     # ✅ İptal & İade Politikası
# #     time_left = ride.departure_time - datetime.utcnow()
# #     refund_percentage = 0.0
# #     if time_left >= timedelta(hours=24):
# #         refund_percentage = 1.0  # 100% refund
# #     elif time_left >= timedelta(hours=12):
# #         refund_percentage = 0.5  # 50% refund

# #     refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

# #     # ✅ İade işlemi, ödeme yöntemine bağlı
# #     if payment.payment_method == "wallet":
# #         passenger.wallet_balance += refund_amount
# #     elif payment.payment_method == "credit_card":
# #         db_payment.refund_payment(db, payment.id)
# #     elif payment.payment_method in ["ideal", "paypal"]:
# #         send_notifications(passenger.id, "Your refund is being processed.")

# #     booking.status = "cancelled"
# #     booking.refund_amount = refund_amount
# #     db.commit()

# #     return {"message": "Booking cancelled", "refund": refund_amount}

# # # ✅ Kullanıcının Rezervasyonlarını Getir
# # @router.get("/{user_id}")
# # def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
# #     """
# #     Retrieves all bookings made by a specific user.
# #     """
# #     bookings = db.query(Booking).filter(Booking.passenger_id == user_id).all()
# #     if not bookings:
# #         raise HTTPException(status_code=404, detail="No bookings found for this user")
# #     return bookings

# # # ✅ Admin: Tüm Rezervasyonları Listele
# # @router.get("/admin/all")
# # def get_all_bookings(db: Session = Depends(get_db)):
# #     """
# #     Retrieves all bookings in the system (Admin only).
# #     """
# #     return db.query(Booking).all()

# # # ✅ Admin: Belirli Bir Yolculuğun Rezervasyonlarını Listele
# # @router.get("/ride/{ride_id}")
# # def get_bookings_for_ride(ride_id: int, db: Session = Depends(get_db)):
# #     """
# #     Retrieves all bookings for a specific ride (Admin only).
# #     """
# #     bookings = db.query(Booking).filter(Booking.ride_id == ride_id).all()
# #     if not bookings:
# #         raise HTTPException(status_code=404, detail="No bookings found for this ride")
# #     return bookings


# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
# from sqlalchemy.orm import Session
# from db import db_booking, db_payment
# from schemas import BookingCreate, BookingDisplay
# from db.database import get_db
# from db.models import User, Ride, Booking, Payment
# from db.enums import PaymentMethod
# from utils.notifications import send_notifications, send_sms
# from datetime import datetime, timedelta

# router = APIRouter(
#     prefix="/bookings",
#     tags=["Bookings"]
# )

# # ✅ Kullanıcı Ödeme Seçerek Yolculuk Rezervasyonu Yapmalı
# @router.post("/book")
# def book_ride(
#     ride_id: int = Form(...),
#     passenger_id: int = Form(...),
#     seats_booked: int = Form(...),
#     payment_method: PaymentMethod = Form(...),  # ✅ Dropdown (Enum)
#     token: str = Form(None),  # ✅ Kredi Kartı için (Opsiyonel)
#     background_tasks: BackgroundTasks = BackgroundTasks(),
#     db: Session = Depends(get_db)
# ):
#     """
#     Kullanıcıların **Cüzdan, Kredi Kartı, PayPal veya iDEAL** ile rezervasyon yapmasını sağlar.
#     """
#     ride = db.query(Ride).filter(Ride.id == ride_id).first()
#     passenger = db.query(User).filter(User.id == passenger_id).first()

#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found")
#     if not passenger:
#         raise HTTPException(status_code=404, detail="Passenger not found")
#     if seats_booked > ride.available_seats:
#         raise HTTPException(status_code=400, detail="Not enough seats available")

#     total_price = ride.price_per_seat * seats_booked

#     # ✅ Ödeme işlemi çağır
#     payment_response = db_payment.make_payment(
#         db=db,
#         user_id=passenger_id,
#         ride_id=ride_id,
#         amount=total_price,
#         payment_method=payment_method,
#         token=token
#     )

#     if payment_response["status"] != "completed":
#         raise HTTPException(status_code=400, detail="Payment failed")

#     # ✅ Rezervasyonu kaydet
#     ride.available_seats -= seats_booked
#     booking = Booking(
#         ride_id=ride_id,
#         passenger_id=passenger_id,
#         seats_booked=seats_booked,
#         booking_source="online",
#         status="confirmed"
#     )
#     db.add(booking)
#     db.commit()

#     # ✅ Arka planda SMS & E-posta bildirimi gönder
#     background_tasks.add_task(send_notifications, passenger.phone, passenger.email)

#     return {"message": "Booking confirmed", "booking_id": booking.id}

# # ✅ Offline Booking (Admin only)
# @router.post("/offline")
# def offline_booking(
#     ride_id: int = Form(...),
#     phone_number: str = Form(...),
#     seats_booked: int = Form(...),
#     background_tasks: BackgroundTasks = BackgroundTasks(),
#     db: Session = Depends(get_db)
# ):
#     """
#     Admin'in, telefonla arayan kullanıcılar için rezervasyon yapmasını sağlar.
#     """
#     ride = db.query(Ride).filter(Ride.id == ride_id).first()

#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found")

#     if seats_booked > ride.available_seats:
#         raise HTTPException(status_code=400, detail="Not enough seats available")

#     ride.available_seats -= seats_booked
#     booking = Booking(
#         ride_id=ride_id,
#         phone_number=phone_number,
#         seats_booked=seats_booked,
#         booking_source="offline",
#         status="confirmed"
#     )
#     db.add(booking)
#     db.commit()

#     # ✅ SMS bildirimi gönder
#     background_tasks.add_task(send_notifications, phone_number, None)

#     return {"message": "Offline booking confirmed", "booking_id": booking.id}

# # ✅ İptal ve Para İadesi (Ödeme Yöntemine Göre)
# @router.post("/{booking_id}/cancel")
# def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
#     """
#     **İptal Politikası:**
#     - **24 saatten fazla varsa** → **%100 iade**
#     - **12-24 saat varsa** → **%50 iade**
#     - **12 saatten az kaldıysa** → **İade yapılmaz**
#     """
#     booking = db.query(Booking).filter(Booking.id == booking_id).first()
#     if not booking:
#         raise HTTPException(status_code=404, detail="Booking not found")
#     if booking.status == "cancelled":
#         raise HTTPException(status_code=400, detail="Booking is already cancelled")

#     ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
#     passenger = db.query(User).filter(User.id == booking.passenger_id).first()
#     payment = db.query(Payment).filter(Payment.ride_id == booking.ride_id, Payment.user_id == booking.passenger_id).first()

#     if not ride or not passenger or not payment:
#         raise HTTPException(status_code=404, detail="Ride, passenger, or payment record not found")

#     # ✅ İptal & İade Politikası
#     time_left = ride.departure_time - datetime.utcnow()
#     refund_percentage = 0.0
#     if time_left >= timedelta(hours=24):
#         refund_percentage = 1.0  # 100% refund
#     elif time_left >= timedelta(hours=12):
#         refund_percentage = 0.5  # 50% refund

#     refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

#     # ✅ İade işlemi, ödeme yöntemine bağlı
#     if payment.payment_method == PaymentMethod.WALLET:
#         passenger.wallet_balance += refund_amount
#     elif payment.payment_method == PaymentMethod.CREDIT_CARD:
#         db_payment.refund_payment(db, payment.id)
#     elif payment.payment_method in [PaymentMethod.IDEAL, PaymentMethod.PAYPAL]:
#         send_notifications(passenger.id, "Your refund is being processed.")

#     booking.status = "cancelled"
#     booking.refund_amount = refund_amount
#     db.commit()

#     return {"message": "Booking cancelled", "refund": refund_amount}

# # ✅ Kullanıcının Rezervasyonlarını Getir
# @router.get("/{user_id}")
# def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
#     """
#     Kullanıcının yaptığı tüm rezervasyonları getirir.
#     """
#     bookings = db.query(Booking).filter(Booking.passenger_id == user_id).all()
#     if not bookings:
#         raise HTTPException(status_code=404, detail="No bookings found for this user")
#     return bookings

# # ✅ Admin: Tüm Rezervasyonları Listele
# @router.get("/admin/all")
# def get_all_bookings(db: Session = Depends(get_db)):
#     """
#     **Admin Kullanıcılar** için sistemdeki tüm rezervasyonları döndürür.
#     """
#     return db.query(Booking).all()

# # ✅ Admin: Belirli Bir Yolculuğun Rezervasyonlarını Listele
# @router.get("/ride/{ride_id}")
# def get_bookings_for_ride(ride_id: int, db: Session = Depends(get_db)):
#     """
#     **Admin Kullanıcılar** için belirli bir yolculuğun rezervasyonlarını getirir.
#     """
#     bookings = db.query(Booking).filter(Booking.ride_id == ride_id).all()
#     if not bookings:
#         raise HTTPException(status_code=404, detail="No bookings found for this ride")
#     return bookings



from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from sqlalchemy.orm import Session
from db import db_payment
from db.database import get_db
from db.models import User, Ride, Booking, Payment
from db.enums import PaymentMethod
from utils.auth import get_current_user  # ✅ Kullanıcı kimliği doğrulama fonksiyonunu içe aktar
from utils.notifications import send_notifications
from datetime import datetime, timedelta
from db.enums import PaymentMethod

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

# ✅ Kullanıcı Ödeme Seçerek Yolculuk Rezervasyonu Yapmalı
from db.enums import PaymentMethod  # ✅ PaymentMethod Enum'unu içe aktar

@router.post("/book")
def book_ride(
    ride_id: int = Form(...),
    seats_booked: int = Form(...),
    payment_method: PaymentMethod = Form(...),  # ✅ Dropdown Enum olarak düzeltildi!
    token: str = Form(None),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcıların **Cüzdan, Kredi Kartı, PayPal veya iDEAL** ile rezervasyon yapmasını sağlar.
    """
    if payment_method == PaymentMethod.CREDIT_CARD and not token:
        raise HTTPException(status_code=400, detail="Credit card payment requires a token")

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    total_price = ride.price_per_seat * seats_booked

    # ✅ Ödeme işlemi çağır
    payment_response = db_payment.make_payment(
        db=db,
        user_id=current_user.id,
        ride_id=ride_id,
        amount=total_price,
        payment_method=payment_method,  # ✅ Enum olarak gönderildi!
        token=token
    )

    if payment_response["status"] != "completed":
        raise HTTPException(status_code=400, detail="Payment failed")

    # ✅ Rezervasyonu kaydet
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

    # ✅ Arka planda SMS & E-posta bildirimi gönder
    background_tasks.add_task(send_notifications, current_user.phone, current_user.email)

    return {"message": "Booking confirmed", "booking_id": booking.id}




# ✅ Offline Booking (Admin only)
@router.post("/offline")
def offline_booking(
    ride_id: int = Form(...),
    phone_number: str = Form(...),
    seats_booked: int = Form(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()  # ✅ `Depends()` kaldırıldı, doğrudan nesne olarak eklendi!
):
    """
    Admin'in, telefonla arayan kullanıcılar için rezervasyon yapmasını sağlar.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()

    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if seats_booked > ride.available_seats:
        raise HTTPException(status_code=400, detail="Not enough seats available")

    ride.available_seats -= seats_booked
    booking = Booking(
        ride_id=ride_id,
        phone_number=phone_number,
        seats_booked=seats_booked,
        booking_source="offline",
        status="confirmed"
    )
    db.add(booking)
    db.commit()

    # ✅ SMS bildirimi gönder
    background_tasks.add_task(send_notifications, phone_number, None)

    return {"message": "Offline booking confirmed", "booking_id": booking.id}

# ✅ İptal ve Para İadesi (Ödeme Yöntemine Göre)
@router.post("/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **İptal Politikası:**
    - **24 saatten fazla varsa** → **%100 iade**
    - **12-24 saat varsa** → **%50 iade**
    - **12 saatten az kaldıysa** → **İade yapılmaz**
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

    # ✅ İptal & İade Politikası
    time_left = ride.departure_time - datetime.utcnow()
    refund_percentage = 0.0
    if time_left >= timedelta(hours=24):
        refund_percentage = 1.0  # 100% refund
    elif time_left >= timedelta(hours=12):
        refund_percentage = 0.5  # 50% refund

    refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

    # ✅ İade işlemi, ödeme yöntemine bağlı
    if payment.payment_method == PaymentMethod.WALLET.value:
        current_user.wallet_balance += refund_amount
    elif payment.payment_method == PaymentMethod.CREDIT_CARD.value:
        db_payment.refund_payment(db, payment.id)
    elif payment.payment_method in [PaymentMethod.IDEAL.value, PaymentMethod.PAYPAL.value]:
        send_notifications(current_user.id, "Your refund is being processed.")

    booking.status = "cancelled"
    booking.refund_amount = refund_amount
    db.commit()

    return {"message": "Booking cancelled", "refund": refund_amount}

# ✅ Kullanıcının Rezervasyonlarını Getir
@router.get("/{user_id}")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    """
    Kullanıcının yaptığı tüm rezervasyonları getirir.
    """
    bookings = db.query(Booking).filter(Booking.passenger_id == user_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this user")
    return bookings

# ✅ Admin: Tüm Rezervasyonları Listele
@router.get("/admin/all")
def get_all_bookings(db: Session = Depends(get_db)):
    """
    **Admin Kullanıcılar** için sistemdeki tüm rezervasyonları döndürür.
    """
    return db.query(Booking).all()

# ✅ Admin: Belirli Bir Yolculuğun Rezervasyonlarını Listele
@router.get("/ride/{ride_id}")
def get_bookings_for_ride(ride_id: int, db: Session = Depends(get_db)):
    """
    **Admin Kullanıcılar** için belirli bir yolculuğun rezervasyonlarını getirir.
    """
    bookings = db.query(Booking).filter(Booking.ride_id == ride_id).all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found for this ride")
    return bookings
