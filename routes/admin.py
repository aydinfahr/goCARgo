# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from db.database import get_db
# from db.models import User
# from db.db_admin import delete_user, ban_user, get_all_bookings, cancel_booking, get_all_reviews, delete_review
# from schemas import UserDisplay, BookingDisplay, ReviewDisplay
# from typing import List
# import logging

# router = APIRouter(
#     prefix="/admin",
#     tags=["Admin"]
# )

# # Log ayarları
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ✅ Admin Authorization - Only Admin Users Can Access
# def admin_required(user: User):
#     if not user.is_admin:
#         raise HTTPException(status_code=403, detail="You do not have admin permissions.")
#     return user

# # ✅ 1️⃣ Get All Users
# def get_all_users(db: Session) -> List[UserDisplay]:
#     users = db.query(User).all()
#     return [UserDisplay.model_validate(user) for user in users]

# # ✅ 2️⃣ Delete User
# @router.delete("/users/{user_id}", response_model=UserDisplay)
# def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         user = db.query(User).filter(User.id == user_id).first()
#         if user is None:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         user_display = UserDisplay.from_orm(user)  
#         db.delete(user)
#         db.commit()
#         return user_display 
        
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")


# # ✅ 3️⃣ Ban / Unban User
# @router.put("/users/{user_id}/ban")
# def ban_user_endpoint(user_id: int, ban_status: bool, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         return ban_user(db, user_id, ban_status)
#     except HTTPException as e:
#         logger.error(f"Hata: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")

# # ✅ 4️⃣ Get All Bookings
# @router.get("/bookings", response_model=List[BookingDisplay])
# def get_all_bookings_endpoint(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         return get_all_bookings(db)
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")

# # ✅ 5️⃣ Cancel a Booking
# @router.put("/bookings/{booking_id}/cancel")
# def cancel_booking_endpoint(booking_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         return cancel_booking(db, booking_id)
#     except HTTPException as e:
#         logger.error(f"Hata: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")

# # ✅ 6️⃣ Get All Reviews
# @router.get("/reviews", response_model=List[ReviewDisplay])
# def get_all_reviews_endpoint(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         return get_all_reviews(db)
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")

# # ✅ 7️⃣ Delete a Review
# @router.delete("/reviews/{review_id}")
# def delete_review_endpoint(review_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         return delete_review(db, review_id)
#     except HTTPException as e:
#         logger.error(f"Hata: {e.detail}")
#         raise e
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")

# # ✅ Get All Users Endpoint
# @router.get("/users", response_model=List[UserDisplay])
# def get_all_users_endpoint(db: Session = Depends(get_db), admin: User = Depends(admin_required)):
#     try:
#         return get_all_users(db)
#     except Exception as e:
#         logger.error(f"Beklenmeyen hata: {e}")
#         raise HTTPException(status_code=500, detail="Bir hata oluştu.")
