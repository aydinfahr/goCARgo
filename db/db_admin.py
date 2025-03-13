# from sqlalchemy.orm import Session
# from db.models import User, Booking, Review
# from schemas import UserDisplay, BookingDisplay, ReviewDisplay
# from fastapi import HTTPException
# from typing import List


# # ✅ 1️⃣ Retrieve All Users
# def get_all_users(db: Session) -> List[UserDisplay]:
#     users = db.query(User).all()
#     return [UserDisplay.model_validate(user) for user in users]

# # ✅ 2️⃣ Delete a User
# def delete_user(db: Session, user_id: int):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     db.delete(user)
#     db.commit()
#     return {"message": "User deleted successfully"}

# # ✅ 3️⃣ Ban / Unban a User
# def ban_user(db: Session, user_id: int, ban_status: bool):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     user.is_banned = ban_status
#     db.commit()
#     return {"message": f"User {'banned' if ban_status else 'unbanned'} successfully"}

# # ✅ 4️⃣ Retrieve All Bookings
# def get_all_bookings(db: Session) -> List[BookingDisplay]:
#     bookings = db.query(Booking).all()
#     return [BookingDisplay.model_validate(booking) for booking in bookings]

# # ✅ 5️⃣ Cancel a Booking
# def cancel_booking(db: Session, booking_id: int):
#     booking = db.query(Booking).filter(Booking.id == booking_id).first()
#     if not booking:
#         raise HTTPException(status_code=404, detail="Booking not found")

#     booking.status = "Cancelled"
#     db.commit()
#     return {"message": "Booking cancelled successfully"}

# # ✅ 6️⃣ Retrieve All Reviews
# def get_all_reviews(db: Session) -> List[ReviewDisplay]:
#     reviews = db.query(Review).all()
#     return [ReviewDisplay.model_validate(review) for review in reviews]

# # ✅ 7️⃣ Delete a Review
# def delete_review(db: Session, review_id: int):
#     review = db.query(Review).filter(Review.id == review_id).first()
#     if not review:
#         raise HTTPException(status_code=404, detail="Review not found")

#     db.delete(review)
#     db.commit()
#     return {"message": "Review deleted successfully"}
