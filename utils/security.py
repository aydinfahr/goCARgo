from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from utils.hashing import verify_password
from sqlalchemy.orm import Session
from db.models import User
from db.database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def authenticate_user(db, username: str, password: str):
    """Authenticates a user by verifying the provided password."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):  # ✅ Şifre doğrulama
        return None
    return user

# ✅ Güvenli JWT için Gizli Anahtar (Gerçek projelerde .env içinde saklanmalı)
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token süresi 30 dakika

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Creates a JWT token with expiration time."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    """Decodes and verifies the JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retrieves the currently authenticated user from JWT token."""
    token_data = verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == token_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
