from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User, Booking, Payment, Review
from schemas import UserDisplay, ReviewDisplay, BookingDisplay, PaymentDisplay
from typing import List

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

# ✅ Admin Authorization - Only Admin Users Can Access
def admin_required(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="You do not have admin permissions.")
    return user

# ✅ 1️⃣ Get All Users
@router.get("/users", response_model=List[UserDisplay])
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Retrieve all users (Admins only).
    """
    users = db.query(User).all()
    return users

# ✅ 2️⃣ Delete User
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Delete a user by ID (Admins only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# ✅ 3️⃣ Ban / Unban User
@router.put("/users/{user_id}/ban")
def ban_user(user_id: int, ban_status: bool, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Ban or Unban a user (Admins only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_banned = ban_status
    db.commit()
    return {"message": f"User {'banned' if ban_status else 'unbanned'} successfully"}

# ✅ 4️⃣ Get All Bookings
@router.get("/bookings", response_model=List[BookingDisplay])
def get_all_bookings(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Retrieve all bookings (Admins only).
    """
    bookings = db.query(Booking).all()
    return bookings

# ✅ 5️⃣ Cancel a Booking
@router.put("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Cancel a booking and issue a refund (Admins only).
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "Cancelled"
    db.commit()
    return {"message": "Booking cancelled successfully"}

# ✅ 6️⃣ Get All Reviews
@router.get("/reviews", response_model=List[ReviewDisplay])
def get_all_reviews(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Retrieve all reviews (Admins only).
    """
    reviews = db.query(Review).all()
    return reviews

# ✅ 7️⃣ Delete a Review
@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
    """
    Delete a review by ID (Admins only).
    """
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}
