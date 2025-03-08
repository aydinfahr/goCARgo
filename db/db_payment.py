from sqlalchemy.orm import Session
from db.models import Payment

# ✅ Kullanıcının ödeme geçmişini getir
def get_payments(db: Session, user_id: int):
    return db.query(Payment).filter(Payment.user_id == user_id).all()

# ✅ Yeni bir ödeme kaydı oluştur
def create_payment(db: Session, user_id: int, ride_id: int, amount: float, status: str):
    new_payment = Payment(
        user_id=user_id,
        ride_id=ride_id,
        amount=amount,
        payment_status=status
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

# ✅ Ödeme durumunu güncelle
def update_payment_status(db: Session, payment_id: int, new_status: str):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None
    payment.payment_status = new_status
    db.commit()
    db.refresh(payment)
    return payment

# ✅ Kullanıcıya geri ödeme yap
def refund_payment(db: Session, payment_id: int):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None

    # Eğer ödeme zaten iade edildiyse işlemi tekrarlama
    if payment.payment_status == "refunded":
        return payment

    payment.payment_status = "refunded"
    db.commit()
    db.refresh(payment)
    return payment
