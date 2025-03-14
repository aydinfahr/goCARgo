from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.db_user import get_users, assign_admin
from schemas import AdminAssign, UserDisplay, UserUpdate, UserDeleteResponse, UserBase
from utils.auth import get_current_user
from utils.hashing import hash_password, verify_password
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

    #  Check if username or email is already registered
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    #  Hash the password
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

    return new_user

# Get all users
@router.get("/", response_model=List[UserDisplay])
def get_all_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can view all users")
    
    return get_users(db)


# ----------------------- 📌 Retrieve User Profile ----------------------- #
@router.get("/{user_id}", response_model=UserDisplay)
def get_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    **Retrieve user profile.**
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")

    return user

# ----------------------- 📌 Update User Profile ----------------------- #
@router.put("/{user_id}", response_model=UserDisplay)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **Update user profile.**
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")


    update_data = user_update.model_dump()
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.patch("/{id}", response_model=UserDisplay)
def admin_assign(
    id: int, 
    request: AdminAssign,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized.Only admins can assign admins")
    
    return assign_admin(id, request, db)


# ----------------------- 📌 Delete User ----------------------- #
@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **Delete a user.**
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")


    db.delete(user)
    db.commit()
    return UserDeleteResponse(message="User deleted successfully")

# ----------------------- 📌 Upload Profile Picture ----------------------- #
@router.post("/{user_id}/upload-avatar")
def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **User uploads their profile picture.**
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    upload_dir = os.path.join("uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, f"{user_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.avatar_url = f"/{file_path}"
    db.commit()
    db.refresh(user)

    return {"message": "Avatar uploaded successfully", "avatar_url": user.avatar_url}
