from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_payment
from schemas import PaymentCreate, PaymentDisplay
from utils.notifications import send_payment_receipt
from utils.notifications import send_system_notifications



router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

# ✅ Kullanıcının ödeme geçmişini getir
@router.get("/{user_id}", response_model=list[PaymentDisplay])
def get_user_payments(user_id: int, db: Session = Depends(get_db)):
    payments = db_payment.get_payments(db, user_id)
    if not payments:
        raise HTTPException(status_code=404, detail="No payment history found")
    return payments

# ✅ Yeni ödeme oluştur
@router.post("/", response_model=PaymentDisplay)
def make_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    payment = db_payment.create_payment(
        db, 
        user_id=payment_data.user_id, 
        ride_id=payment_data.ride_id, 
        amount=payment_data.amount, 
        status="completed"
    )
    return payment

# ✅ Ödeme durumunu güncelle
@router.put("/{payment_id}/status", response_model=PaymentDisplay)
def update_payment_status(payment_id: int, new_status: str, db: Session = Depends(get_db)):
    payment = db_payment.update_payment_status(db, payment_id, new_status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

# ✅ Para iadesi yap
@router.post("/{payment_id}/refund", response_model=PaymentDisplay)
def refund_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db_payment.refund_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or already refunded")
    return payment
