from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas import UserDisplay, UserUpdate, UserDeleteResponse, UserBase
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.notifications import send_email
import shutil
import os

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
    **Creates a new user registration and returns a JWT access token.**
    - Password is hashed using bcrypt.
    """

    # ✅ Check if username or email is already registered
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    # ✅ Hash the password
    hashed_pw = hash_password(request.password)

    new_user = User(
        username=request.username,
        email=request.email,
        password=hashed_pw,
        full_name=request.full_name,
        agreed_terms=request.agreed_terms
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ Generate JWT Token
    access_token = create_access_token(new_user.id)

    # # 📩 Send welcome email
    # send_email(request.email, "Welcome to goCARgo!", "Thanks for signing up!")

    # return {"user": new_user, "access_token": access_token}
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
@router.put("/{user_id}/update", response_model=UserDisplay)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    **Update user profile.**
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

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
