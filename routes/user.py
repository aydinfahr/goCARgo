from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from pydantic import EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.enums import UserRole
from schemas import UserDisplay, UserUpdate, UserDeleteResponse, AuthResponse
from utils.auth import hash_password, verify_password, create_access_token, get_current_user, generate_verification_code, verify_verification_code
from utils.notifications import send_email

import shutil
import os
import uuid

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ----------------------- 📌 User Registration (Supports Profile Picture) ----------------------- #
@router.post("/register", response_model=AuthResponse)
def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: UserRole = Form(...),
    agreed_terms: bool = Form(...),
    avatar: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """
    **Yeni bir kullanıcı kaydeder.**  
    - **role:** Kullanıcı rolü (Enum - Dropdown)  
    - **avatar:** Opsiyonel profil resmi yükleme  
    - **agreed_terms:** Kullanıcının kuralları kabul ettiğini doğrular  
    """

    # 📌 Mevcut kullanıcı kontrolü
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    # 📌 Şifreyi hashle
    hashed_pw = hash_password(password)

    # 📌 Profil fotoğrafı kaydet
    avatar_path = None
    if avatar:
        upload_dir = "uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)
        avatar_path = f"{upload_dir}/{username}_{avatar.filename}"

        with open(avatar_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)

    # 📌 Kullanıcıyı oluştur
    new_user = User(
        username=username,
        email=email,
        password=hashed_pw,
        full_name=full_name,
        role=role.value,  # Enum olarak kaydedildi
        verified_email=False,
        agreed_terms=agreed_terms,
        profile_picture=avatar_path,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 📌 JWT Token oluştur
    access_token = create_access_token(new_user.id, new_user.role)

    # 📩 Kullanıcıya doğrulama kodu gönder
    verification_code = generate_verification_code()
    new_user.verification_code = verification_code
    db.commit()

    email_subject = "Verify Your Email"
    email_content = f"Your verification code is: {verification_code}"
    email_sent = send_email(new_user.email, email_subject, email_content)

    if not email_sent:
        print("🚨 Email Sending Failed!")
        raise HTTPException(status_code=500, detail="Could not send verification email.")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserDisplay.from_orm(new_user),
    }

# ----------------------- 📌 User Login ----------------------- #
@router.post("/login")
def login_user(
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    """
    Allows a user to log in and receive a JWT token.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(db_user.id, db_user.role)
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------------- 📌 Get User Profile ----------------------- #
@router.get("/{user_id}", response_model=UserDisplay)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows **only the user themselves or an admin** to access user details.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")

    return user

# ----------------------- 📌 Update User Profile ----------------------- #
@router.put("/{user_id}/update", response_model=UserDisplay)
def update_user(
    user_id: int,
    current_username: str = Form(...),
    new_username: Optional[str] = Form(None),
    current_email: str = Form(...),
    new_email: Optional[str] = Form(None),
    new_full_name: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    **Allows only the user themselves or an admin to update user details.**
    - Requires **current username & email** to verify identity.
    - Supports **optional username, email, and profile picture update**.
    - Sends **verification email** when a new email is set.
    """

    # 🔍 Fetch user from DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔐 Ensure only the user or an admin can update
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    # ✅ Verify identity before allowing updates
    if user.username != current_username or user.email != current_email:
        raise HTTPException(status_code=400, detail="Current username or email is incorrect")

    # ✅ Handle Email Update (Send Verification Email)
    if new_email and new_email != user.email:
        verification_code = str(uuid.uuid4())  # Generate a unique verification code
        user.email = new_email
        user.verified_email = False  # Set email as unverified

        # 📩 Send verification email with a unique link
        verification_link = f"http://127.0.0.1:8000/users/verify-email?email={new_email}&code={verification_code}"
        send_email(
            new_email,
            "Verify Your New Email",
            f"Click the link to verify your email: {verification_link}"
        )

    # ✅ Update other fields only if provided
    if new_username:
        user.username = new_username
    if new_full_name:
        user.full_name = new_full_name

    # ✅ Handle profile picture upload
    if profile_picture:
        upload_dir = "uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)

        avatar_path = f"{upload_dir}/{user.id}_{profile_picture.filename}"
        with open(avatar_path, "wb") as buffer:
            shutil.copyfileobj(profile_picture.file, buffer)

        user.profile_picture = avatar_path  # ✅ Save new profile picture

    # ✅ Commit changes to DB
    db.commit()
    db.refresh(user)
    return user



# ----------------------- 📌 Delete User ----------------------- #
@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows **only the user themselves or an admin** to delete a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.delete(user)
    db.commit()
    return UserDeleteResponse(message="User deleted successfully")

# ----------------------- 📌 Reset Password ----------------------- #
@router.post("/reset-password")
def reset_password(email: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows a **user to reset their password** after verifying identity.
    """
    if current_user.email != email and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to reset password for this user")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

# ----------------------- 📌 ADMIN: Get All Users ----------------------- #
@router.get("/admin/all")
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **Only admins can retrieve all users.**
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(User).all()



@router.get("/verify-email")
def verify_email(
    email: str = Query(..., description="User's email for verification"),
    code: Optional[str] = Query(None, description="Verification code (leave empty and click 'Get Code' to receive a new one)"),
    db: Session = Depends(get_db)
):
    """
    Verifies the user's email using the provided verification code.
    
    - **If code is empty**, a new code is generated and sent to the user's email.  
    - **If code is provided**, it checks if the code is valid.  
    - **Swagger UI now has a 'Get Code' button to request a new code.**
    """

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not code:
        # ✅ "Get Code" işlemi: Yeni doğrulama kodu oluştur ve e-posta gönder
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        db.commit()

        send_email(email, "Your Verification Code", f"Your verification code is: {verification_code}")

        return {"message": "Verification code sent to email.", "code": verification_code}

    # ✅ Kullanıcı bir kod girdiyse, kodun doğruluğunu kontrol et
    if user.verification_code is None or user.verification_code != code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    # ✅ Doğrulama başarılıysa, kullanıcının `verified_email` alanını güncelle
    user.verified_email = True
    user.verification_code = None  # Kodu sıfırla
    db.commit()

    return {"message": "Email successfully verified"}
