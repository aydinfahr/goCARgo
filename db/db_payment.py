from sqlalchemy.orm import Session
from db.models import Payment, User
from db.enums import PaymentStatus, PaymentMethod
from fastapi import HTTPException
import stripe

# ✅ Stripe API Anahtarı (Env Değişkenlerinden Al)
stripe.api_key = "STRIPE_SECRET_KEY"

# ✅ Kullanıcının ödeme geçmişini getir
def get_payments(db: Session, user_id: int):
    return db.query(Payment).filter(Payment.user_id == user_id).all()

# ✅ Tekil ödeme kaydını getir
def get_payment_by_id(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()

# ✅ Yeni bir ödeme yap ve kaydet
def make_payment(db: Session, user_id: int, ride_id: int, amount: float, payment_method: PaymentMethod, token: str = None):
    """
    Kullanıcının seçtiği ödeme yöntemine göre ödeme yapar ve veritabanına kaydeder.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    charge_id = None

    if payment_method == PaymentMethod.WALLET:
        if user.wallet_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        user.wallet_balance -= amount
        db.commit()

    elif payment_method == PaymentMethod.CREDIT_CARD:
        if not token:
            raise HTTPException(status_code=400, detail="Credit card token is required for this payment method")
        
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Stripe cent olarak kabul ediyor
                currency="eur",
                source=token,
                description=f"Payment for Ride ID {ride_id}",
            )
            charge_id = charge["id"]
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe payment failed: {str(e)}")

    elif payment_method in [PaymentMethod.IDEAL, PaymentMethod.PAYPAL]:
        # Simülasyon için direkt başarılı kabul edelim.
        pass

    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")

    # ✅ Ödeme Kaydını Veritabanına Kaydet
    new_payment = Payment(
        user_id=user_id,
        ride_id=ride_id,
        amount=amount,
        payment_status=PaymentStatus.COMPLETED,
        payment_method=payment_method,
        charge_id=charge_id
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {"status": "completed", "message": "Payment successful", "payment_id": new_payment.id}

# ✅ Ödeme durumunu güncelle
def update_payment_status(db: Session, payment_id: int, new_status: PaymentStatus):
    """
    Updates the status of an existing payment record.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment.payment_status = new_status
    db.commit()
    db.refresh(payment)
    return payment

# ✅ Kullanıcıya geri ödeme yap
def refund_payment(db: Session, payment_id: int):
    """
    Processes a refund based on the original payment method.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.payment_status == PaymentStatus.REFUNDED:
        return payment  # Eğer zaten iade edilmişse işlemi tekrar yapma

    user = db.query(User).filter(User.id == payment.user_id).first()

    # ✅ Wallet üzerinden ödeme yapıldıysa, cüzdana geri yükleme yap
    if payment.payment_method == PaymentMethod.WALLET:
        user.wallet_balance += payment.amount
        payment.payment_status = PaymentStatus.REFUNDED
        db.commit()
        db.refresh(user)
        db.refresh(payment)
        return payment

    # ✅ Stripe Kredi Kartı üzerinden ödeme yapıldıysa, Stripe üzerinden geri ödeme yap
    elif payment.payment_method == PaymentMethod.CREDIT_CARD:
        if not payment.charge_id:
            raise HTTPException(status_code=400, detail="Charge ID missing for refund")
        
        try:
            stripe.Refund.create(charge=payment.charge_id)
            payment.payment_status = PaymentStatus.REFUNDED
            db.commit()
            db.refresh(payment)
            return payment
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=f"Stripe refund failed: {str(e)}")

    # ✅ iDEAL veya PayPal üzerinden ödeme yapıldıysa, manuel olarak işaretle
    elif payment.payment_method in [PaymentMethod.IDEAL, PaymentMethod.PAYPAL]:
        payment.payment_status = PaymentStatus.REFUND_PENDING  # İade beklemede
        db.commit()
        db.refresh(payment)
        return payment

    return None
