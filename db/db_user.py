from sqlalchemy.orm import Session
from db.models import User
from schemas import UserCreate, UserUpdate
from utils.hashing import hash_password  # ✅ Secure password hashing
from fastapi import HTTPException, Depends
from utils.auth import get_current_user  # ✅ Authorization for user actions

def create_user(db: Session, user_data: UserCreate):
    """
    Creates a new user with a hashed password.
    """
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username is already registered.")

    hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role.value,  # ✅ Enum string olarak kaydedildi
        verified_email=False,
        verified_id=False,
        profile_picture=user_data.profile_picture
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def get_user_by_id(db: Session, user_id: int, current_user: User = Depends(get_current_user)):
    """
    Fetches a user by their unique ID (only the user themselves or an admin can access).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this user")

    return user


def get_user_by_email(db: Session, email: str, current_user: User = Depends(get_current_user)):
    """
    Fetches a user by their email (admin or the user themselves).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.email != email and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this user")

    return user


def update_user(db: Session, user_id: int, user_update_data: UserUpdate, current_user: User = Depends(get_current_user)):
    """
    Updates user information (only the user themselves or an admin can update).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    if user_update_data.email and user_update_data.email != user.email:
        existing_email = db.query(User).filter(User.email == user_update_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email is already in use.")

    if user_update_data.username and user_update_data.username != user.username:
        existing_username = db.query(User).filter(User.username == user_update_data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username is already in use.")

    for key, value in user_update_data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user: User = Depends(get_current_user)):
    """
    Deletes a user from the database (only admin or the user themselves can delete their account).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


def verify_user_email(db: Session, user_id: int, current_user: User = Depends(get_current_user)):
    """
    Marks a user's email as verified (only admin or the user themselves).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to verify this user's email")

    user.verified_email = True
    db.commit()
    db.refresh(user)
    return user


def verify_user_id(db: Session, user_id: int, current_user: User = Depends(get_current_user)):
    """
    Marks a user's ID verification as completed (only admin or the user themselves).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to verify this user's ID")

    user.verified_id = True
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user_id: int, new_password: str, current_user: User = Depends(get_current_user)):
    """
    Allows a user to change their password (only the user themselves).
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to change password for this user")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}
