# import stripe
# from fastapi import APIRouter, Depends, HTTPException, Form
# from sqlalchemy.orm import Session
# from db.database import get_db
# from db import db_payment
# from db.models import User, PaymentStatus
# from schemas import PaymentCreate, PaymentDisplay, PaymentRequest
# from utils.auth import get_current_user
# from utils.notifications import send_payment_receipt
# from utils.notifications import send_system_notifications



# router = APIRouter(
#     prefix="/payments",
#     tags=["Payments"]
# )


# # ✅ Stripe API Anahtarını Buraya Ekleyin
# stripe.api_key = "STRIPE_SECRET_KEY"

# # ✅ Desteklenen ödeme yöntemleri (Dropdown için)
# SUPPORTED_PAYMENT_METHODS = ["wallet", "credit_card", "ideal", "paypal"]



# # ✅ Yeni ödeme oluştur
# @router.post("/", response_model=PaymentDisplay)
# def make_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
#     payment = db_payment.create_payment(
#         db, 
#         user_id=payment_data.user_id, 
#         ride_id=payment_data.ride_id, 
#         amount=payment_data.amount, 
#         status="completed"
#     )
#     return payment


# # ✅ Kullanıcının ödeme geçmişini getir
# @router.get("/{user_id}", response_model=list[PaymentDisplay])
# def get_user_payments(user_id: int, db: Session = Depends(get_db)):
#     payments = db_payment.get_payments(db, user_id)
#     if not payments:
#         raise HTTPException(status_code=404, detail="No payment history found")
#     return payments


# # ✅ Ödeme durumunu güncelle
# @router.put("/{payment_id}/status", response_model=PaymentDisplay)
# def update_payment_status(payment_id: int, new_status: str, db: Session = Depends(get_db)):
#     payment = db_payment.update_payment_status(db, payment_id, new_status)
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found")
#     return payment

# # ✅ Para iadesi yap
# @router.post("/{payment_id}/refund", response_model=PaymentDisplay)
# def refund_payment(payment_id: int, db: Session = Depends(get_db)):
#     payment = db_payment.refund_payment(db, payment_id)
#     if not payment:
#         raise HTTPException(status_code=404, detail="Payment not found or already refunded")
#     return payment


import stripe
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_payment
from db.models import User, PaymentStatus
from schemas import PaymentCreate, PaymentDisplay, PaymentRequest
from utils.auth import get_current_user
from utils.notifications import send_payment_receipt, send_system_notifications

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

# ✅ Stripe API Anahtarı
stripe.api_key = "STRIPE_SECRET_KEY"

# ✅ Desteklenen ödeme yöntemleri (Dropdown için)
SUPPORTED_PAYMENT_METHODS = ["wallet", "credit_card", "ideal", "paypal"]

# ✅ Ödeme oluşturma ve işleme
@router.post("/", response_model=PaymentDisplay)
def make_payment(
    ride_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),  # ✅ Dropdown için
    token: str = Form(None),  # Kredi Kartı için Stripe Token
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcı seçtiği ödeme yöntemi ile ödeme yapar.
    """
    if payment_method not in SUPPORTED_PAYMENT_METHODS:
        raise HTTPException(status_code=400, detail=f"Invalid payment method. Supported: {SUPPORTED_PAYMENT_METHODS}")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # ✅ Wallet ile ödeme
    if payment_method == "wallet":
        if current_user.wallet_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        current_user.wallet_balance -= amount
        db.commit()
        db.refresh(current_user)

        payment = db_payment.create_payment(db, user_id=current_user.id, ride_id=ride_id, amount=amount, status="completed")
        send_payment_receipt(current_user.email, amount, "wallet")
        return payment

    # ✅ Kredi Kartı ile ödeme (Stripe)
    elif payment_method == "credit_card":
        if not token:
            raise HTTPException(status_code=400, detail="Credit card token required for this payment method")
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Stripe, kuruş bazında çalışır
                currency="eur",
                source=token,
                description=f"Payment by {current_user.username}"
            )
            payment = db_payment.create_payment(db, user_id=current_user.id, ride_id=ride_id, amount=amount, status="completed")
            send_payment_receipt(current_user.email, amount, "credit_card")
            return payment
        except stripe.error.CardError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ✅ iDEAL ile ödeme
    elif payment_method == "ideal":
        payment = db_payment.create_payment(db, user_id=current_user.id, ride_id=ride_id, amount=amount, status="pending")
        send_system_notifications(current_user.id, "Your iDEAL payment is being processed.")
        return {"message": "iDEAL payment initiated", "payment_id": payment.id}

    # ✅ PayPal ile ödeme
    elif payment_method == "paypal":
        payment = db_payment.create_payment(db, user_id=current_user.id, ride_id=ride_id, amount=amount, status="pending")
        send_system_notifications(current_user.id, "Your PayPal payment is being processed.")
        return {"message": "PayPal payment initiated", "payment_id": payment.id}

    else:
        raise HTTPException(status_code=400, detail="Unsupported payment method")

# ✅ Kullanıcının ödeme geçmişini getir
@router.get("/{user_id}", response_model=list[PaymentDisplay])
def get_user_payments(user_id: int, db: Session = Depends(get_db)):
    payments = db_payment.get_payments(db, user_id)
    if not payments:
        raise HTTPException(status_code=404, detail="No payment history found")
    return payments

# ✅ Ödeme durumunu güncelle
@router.put("/{payment_id}/status", response_model=PaymentDisplay)
def update_payment_status(payment_id: int, new_status: str, db: Session = Depends(get_db)):
    payment = db_payment.update_payment_status(db, payment_id, new_status)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

# ✅ Para iadesi yap
@router.post("/{payment_id}/refund", response_model=PaymentDisplay)
def refund_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Kullanıcıya ödeme iadesi yapar.
    """
    payment = db_payment.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status == "refunded":
        raise HTTPException(status_code=400, detail="Payment already refunded")

    # ✅ Wallet üzerinden ödeme iadesi
    if payment.payment_method == "wallet":
        user = db.query(User).filter(User.id == payment.user_id).first()
        user.wallet_balance += payment.amount
        db.commit()
        db.refresh(user)

    # ✅ Stripe (Kredi Kartı) üzerinden ödeme iadesi
    elif payment.payment_method == "credit_card":
        try:
            stripe.Refund.create(charge=payment.charge_id)
        except stripe.error.StripeError:
            raise HTTPException(status_code=400, detail="Stripe refund failed")

    # ✅ iDEAL ve PayPal ödemelerinde iade
    elif payment.payment_method in ["ideal", "paypal"]:
        send_system_notifications(payment.user_id, "Your refund is being processed.")

    # ✅ Ödeme durumu güncelleme
    payment = db_payment.update_payment_status(db, payment.id, "refunded")
    return {"message": "Refund successful", "new_status": payment.status}
