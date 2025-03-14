


from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form, Response, status
from sqlalchemy.orm import Session
from db import db_payment
from db.database import get_db
from db.models import User, Ride, Booking, Payment
from db.enums import PaymentMethod, SearchType
from schemas import BookingBase, BookingDisplay, BookingStatusUpdate
from utils.auth import get_current_user 
from utils.notifications import send_notifications
from datetime import datetime, timedelta
from db.enums import PaymentMethod
from db.enums import PaymentMethod
from db import db_booking
from utils.auth import get_current_user

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


@router.post('/', response_model=BookingDisplay)  
def create_booking(request: BookingBase, db: Session=Depends(get_db)):
    return db_booking.create_booking(db, request)

# --------------------------------------------------------------------------------

@router.get("/", response_model=list[BookingDisplay])
def get_all_bookings(
    id_type: Optional[SearchType] = None, 
    searched_id : Optional[int] = None, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    if id_type == SearchType.passanger_id:
        if searched_id != current_user and not current_user.is_admin:
            raise HTTPException(status_code=403, detail="You are not authorized")
        return db.query(Booking).filter(Booking.passenger_id == searched_id).all()


    if id_type == SearchType.ride_id and not current_user.is_admin:
        user_id = db.query(Ride).filter(Ride.id == searched_id).first().driver_id
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not authorized")
        return db.query(Booking).filter(Booking.ride_id == searched_id).all()
    
    return db.query(Booking).all()


@router.patch("/{booking_id}", response_model=BookingDisplay)
def update_booking_status(
    booking_id: int, 
    request: BookingStatusUpdate,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    
    if not current_user.is_admin:
        if request.driver_id:
            if request.driver_id != current_user.id:
                raise HTTPException(status_code=403, detail="You are not authorized to update this booking.") 

    # booking = db.query(Booking).filter(Booking.id == booking_id).first()
    # if not booking:
    #     raise HTTPException(status_code=404, detail="Booking not found")

    # ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
    # if not ride:
    #     raise HTTPException(status_code=404, detail="Ride not found")

    # if ride.driver_id != request.driver_id:
    #     raise HTTPException(status_code=403, detail="You are not authorized to update this booking.")

    return db_booking.update_booking_status(db, booking_id, request.status)


@router.put("/{booking_id}", response_model=BookingDisplay)
def update_booking(
    booking_id: int, 
    request: BookingBase, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if  not current_user.is_admin and booking.passenger_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this booking")
    return db_booking.update_booking(db, booking_id, request)




# @router.get("/", response_model=list[BookingDisplay])
# def get_all_bookings(passanger_id: Optional[int] = None , ride_id: Optional[int] = None , db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     if not current_user.is_admin:
#         return db_booking.get_all_bookings(db, passanger_id)
    
#     if passanger_id != current_user.id:
#         raise HTTPException(status_code=403, detail="You are not authorized to view all bookings")
    
#     return db_booking.get_all_bookings(db)

@router.get("/{booking_id}", response_model=BookingDisplay)
def get_booking_by_id(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db_booking.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if not current_user.is_admin and booking.passenger_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to view this booking")
    return booking

# Delete booking
@router.delete("/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if not current_user.is_admin and booking.passenger_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this booking")
    db.delete(booking)
    db.commit()
    background_tasks.add_task(send_notifications, current_user.phone, current_user.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)





# --------------------------------------------------------------------------------

@router.patch("/{booking_id}", response_model=BookingDisplay)
def update_booking_status(
    booking_id: int, 
    request: BookingStatusUpdate,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    
    if not current_user.is_admin:
        if request.driver_id:
            if request.driver_id != current_user.id:
                raise HTTPException(status_code=403, detail="You are not authorized to update this booking.") 

    # booking = db.query(Booking).filter(Booking.id == booking_id).first()
    # if not booking:
    #     raise HTTPException(status_code=404, detail="Booking not found")

    # ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
    # if not ride:
    #     raise HTTPException(status_code=404, detail="Ride not found")

    # if ride.driver_id != request.driver_id:
    #     raise HTTPException(status_code=403, detail="You are not authorized to update this booking.")

    return db_booking.update_booking_status(db, booking_id, request.status)









# @router.post("/book")
# def book_ride(
#     ride_id: int = Form(...),
#     seats_booked: int = Form(...),
#     payment_method: PaymentMethod = Form(...),  # ✅ Dropdown Enum olarak düzeltildi!
#     token: str = Form(None),
#     db: Session = Depends(get_db),
#     background_tasks: BackgroundTasks = BackgroundTasks(),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Kullanıcıların **Cüzdan, Kredi Kartı, PayPal veya iDEAL** ile rezervasyon yapmasını sağlar.
#     """
#     if payment_method == PaymentMethod.CREDIT_CARD and not token:
#         raise HTTPException(status_code=400, detail="Credit card payment requires a token")

#     ride = db.query(Ride).filter(Ride.id == ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found")
#     total_price = ride.price_per_seat * seats_booked

#     # ✅ Ödeme işlemi çağır
#     payment_response = db_payment.make_payment(
#         db=db,
#         user_id=current_user.id,
#         ride_id=ride_id,
#         amount=total_price,
#         payment_method=payment_method,  # ✅ Enum olarak gönderildi!
#         token=token
#     )

#     if payment_response["status"] != "completed":
#         raise HTTPException(status_code=400, detail="Payment failed")

#     # ✅ Rezervasyonu kaydet
#     ride.available_seats -= seats_booked
#     booking = Booking(
#         ride_id=ride_id,
#         passenger_id=current_user.id,
#         seats_booked=seats_booked,
#         booking_source="online",
#         status="confirmed"
#     )
#     db.add(booking)
#     db.commit()

#     # ✅ Arka planda SMS & E-posta bildirimi gönder
#     background_tasks.add_task(send_notifications, current_user.phone, current_user.email)

#     return {"message": "Booking confirmed", "booking_id": booking.id}



# # ✅ İptal ve Para İadesi (Ödeme Yöntemine Göre)
# @router.post("/{booking_id}/cancel")
# def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """
#     **İptal Politikası:**
#     - **24 saatten fazla varsa** → **%100 iade**
#     - **12-24 saat varsa** → **%50 iade**
#     - **12 saatten az kaldıysa** → **İade yapılmaz**
#     """
#     booking = db.query(Booking).filter(Booking.id == booking_id, Booking.passenger_id == current_user.id).first()
#     if not booking:
#         raise HTTPException(status_code=404, detail="Booking not found or unauthorized")
#     if booking.status == "cancelled":
#         raise HTTPException(status_code=400, detail="Booking is already cancelled")

#     ride = db.query(Ride).filter(Ride.id == booking.ride_id).first()
#     payment = db.query(Payment).filter(Payment.ride_id == booking.ride_id, Payment.user_id == current_user.id).first()

#     if not ride or not payment:
#         raise HTTPException(status_code=404, detail="Ride or payment record not found")

#     # ✅ İptal & İade Politikası
#     time_left = ride.departure_time - datetime.utcnow()
#     refund_percentage = 0.0
#     if time_left >= timedelta(hours=24):
#         refund_percentage = 1.0  # 100% refund
#     elif time_left >= timedelta(hours=12):
#         refund_percentage = 0.5  # 50% refund

#     refund_amount = ride.price_per_seat * booking.seats_booked * refund_percentage

#     # ✅ İade işlemi, ödeme yöntemine bağlı
#     if payment.payment_method == PaymentMethod.WALLET.value:
#         current_user.wallet_balance += refund_amount
#     elif payment.payment_method == PaymentMethod.CREDIT_CARD.value:
#         db_payment.refund_payment(db, payment.id)
#     elif payment.payment_method in [PaymentMethod.IDEAL.value, PaymentMethod.PAYPAL.value]:
#         send_notifications(current_user.id, "Your refund is being processed.")

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
