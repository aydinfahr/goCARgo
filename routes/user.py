from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas import UserDisplay, UserUpdate, UserDeleteResponse, UserBase, UserPasswordUpdate
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.notifications import send_email
import shutil
import os
from datetime import datetime
from utils.dependencies import get_current_user



router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ----------------------- 📌 User Registration (Form + JWT) ----------------------- #
@router.post("/register", response_model=UserDisplay)
def register_user(
    request: UserBase,
    db: Session = Depends(get_db)
):
    """
    ✅ Creates a new user registration and returns user data.
    - Password is hashed using bcrypt.
    - Ensures the user has accepted terms & conditions before registering.
    """

    # ✅ Ensure user has accepted the terms
    if not request.agreed_terms:
        raise HTTPException(status_code=400, detail="❌ You must accept the terms and conditions to register.")

    # ✅ Check if username or email is already registered
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="❌ Username or Email already registered.")

    # ✅ Hash the password before storing
    hashed_pw = hash_password(request.password)

    # ✅ Create a new user
    new_user = User(
        username=request.username,
        email=request.email,
        password=hashed_pw,
        full_name=request.full_name,
        agreed_terms=request.agreed_terms,
        is_admin=False,  # Default user role
        is_banned=False,  # Default: Not banned
        rating=0.0,  # Default rating
        rating_count=0,  # Default rating count
        verified_id=False,  # Default: ID not verified
        verified_email=False,  # Default: Email not verified
        member_since=datetime.utcnow()  # Set registration date
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ Return the newly created user
    return new_user


# ----------------------- 📌 Retrieve User Profile ----------------------- #
@router.get("/{user_id}", response_model=UserDisplay)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    **Retrieve user profile.**
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# ----------------------- 📌 Update User Profile ----------------------- #
@router.put("/{user_id}", response_model=UserDisplay)
def update_user(
    user_id: int,
    request: UserUpdate,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="❌ User not found.")

    if request.username:
        user.username = request.username
    if request.email:
        user.email = request.email
    if request.full_name:
        user.full_name = request.full_name

    db.commit()
    db.refresh(user)

    return user

@router.put("/{user_id}/change-password")
def change_password(
    user_id: int,
    request: UserPasswordUpdate,
    db: Session = Depends(get_db)
):
   
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="❌ User not found.")

    # ✅ Verify old password before allowing the change
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=400, detail="❌ Incorrect same with old password.")

    # ✅ Hash new password before saving
    user.password = hash_password(request.new_password)
    db.commit()

    return {"message": "✅ Password updated successfully."}

# ----------------------- 📌 Delete User ----------------------- #
@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    **Delete a user.**
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return UserDeleteResponse(message="User deleted successfully")

# ----------------------- 📌 Upload Profile Picture ----------------------- #
@router.post("/{user_id}/upload-avatar")
def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    **User uploads their profile picture.**
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    upload_dir = os.path.join("uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{user_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.avatar_url = f"/{file_path}"
    db.commit()
    db.refresh(user)

    return {"message": "Avatar uploaded successfully", "avatar_url": user.avatar_url}
