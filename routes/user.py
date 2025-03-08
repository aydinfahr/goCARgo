from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas import UserCreate, UserRole, UserLogin, UserDisplay, UserUpdate, UserDeleteResponse
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.notifications import send_email
import shutil
import os

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 📌 Kullanıcı Kayıt (Form Kullanımı)
@router.post("/register", response_model=UserDisplay)
def register_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: UserRole = Form(...),  # ✅ Dropdown sayesinde sadece doğru roller seçilebilir.
    agreed_terms: bool = Form(...),
    db: Session = Depends(get_db),
):
    """
    Registers a new user and ensures unique username & email.
    """

    # ✅ Kullanıcı adı veya email daha önce kayıtlı mı?
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or Email already registered"
        )

    # ✅ Şifreyi güvenli bir şekilde hashle
    hashed_pw = hash_password(password)

    # ✅ Yeni kullanıcı oluştur
    new_user = User(
        username=username,
        email=email,
        password=hashed_pw,
        full_name=full_name,
        role=role,
        verified_email=False,
        agreed_terms=agreed_terms
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 📩 Hoş geldin e-postası gönder
    send_email(email, "Welcome to goCARgo!", "Thanks for signing up!")

    return new_user


# 📌 Kullanıcı Girişi (JWT Token Döndürme)
@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user.id), "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# 📌 Kullanıcı Profili Görüntüleme
@router.get("/{user_id}", response_model=UserDisplay)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a user's profile information.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 📌 Kullanıcı Profili Güncelleme
@router.put("/{user_id}/update", response_model=UserDisplay)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Updates user profile details.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Only the user themselves or an admin can update an account
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

# 📌 Kullanıcı Silme (Sadece Admin veya Kullanıcının Kendisi)
@router.delete("/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deletes a user from the system. Only an admin or the user themselves can delete the account.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Only the user themselves or an admin can delete an account
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    db.delete(user)
    db.commit()
    return UserDeleteResponse(message="User deleted successfully")

# 📌 Profil Resmi Yükleme
@router.post("/{user_id}/upload-avatar")
def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Allows users to upload a profile picture.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{user_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user.avatar_url = f"/{file_path}"
    db.commit()
    db.refresh(user)

    return {"message": "Avatar uploaded successfully", "avatar_url": user.avatar_url}

# 📌 Şifre Sıfırlama
@router.post("/reset-password")
def reset_password(email: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """
    Resets user password after identity verification.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

# 📌 Admin: Tüm Kullanıcıları Listele
@router.get("/admin/all")
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves all users (Admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    users = db.query(User).all()
    return users
