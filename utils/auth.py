import os
import random
import string
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from db.enums import UserRole  # ✅ ENUM Kullanımı için ayrı dosyadan al
from dotenv import load_dotenv
from schemas import UserDisplay, TokenData
import logging
from fastapi import Security

logger = logging.getLogger(__name__)


# ✅ Ortam değişkenlerini yükle (.env dosyasından)
load_dotenv()

# ✅ Parola Hashleme (Bcrypt kullanarak güvenli şifreleme)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ JWT Token Konfigürasyonu
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # 📌 .env içinde olmalı!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# ✅ OAuth2 Şeması (JWT ile kimlik doğrulama)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# ------------------------ 🔐 Parola İşlemleri ------------------------ #

def hash_password(password: str) -> str:
    """
    Girilen parolayı bcrypt ile hashler.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Girilen parolanın, hashlenmiş parola ile eşleşip eşleşmediğini kontrol eder.
    """
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------ 🔑 JWT Token Yönetimi ------------------------ #

def create_access_token(user_id: int, role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
    """
    Kullanıcı ID'si ve rolüne göre JWT erişim token'ı oluşturur.
    """
    payload = {"sub": str(user_id), "role": role.value}  # ✅ ENUM'un `.value` değerini saklıyoruz
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expire})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, credentials_exception, db: Session):
    """
    Decodes and verifies the JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")

        if not user_id or not user_role:
            raise credentials_exception

        # ✅ Fetch the user from the database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise credentials_exception

        # ✅ Ensure role is an ENUM
        try:
            user.role = UserRole(user_role)  # Convert to Enum
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role format in token.")

        return user
    except JWTError:
        raise credentials_exception


# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     print(f"🔍 DEBUG: Received Token = {token}")  # Token'ı yazdır
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#         token_data = TokenData(user_id=user_id)
#     except JWTError:
#         raise credentials_exception

#     user = db.query(User).filter(User.id == token_data.user_id).first()
#     if user is None:
#         raise credentials_exception

#     print(f"✅ DEBUG: Authenticated User = {user.username}, Role = {user.role}")
#     return user


def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current authenticated user based on JWT token.
    """
    logger.info(f"🔍 Received Token: {token}")  # Token bilgisini logla

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = verify_token(token, credentials_exception, db)
    
    if not user:
        raise credentials_exception

    logger.info(f"✅ Authenticated User: {user.username}, Role: {user.role}")
    return user



# def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
#     """
#     Ensures that only users with the DRIVER role can proceed.
#     """

#     # 🟡 DEBUG: Log user details
#     print(f"🟡 DEBUG: Authenticated User: {current_user.username}, Role: {current_user.role}")

#     # ✅ Ensure role is an ENUM (some databases may store ENUM as string)
#     if not isinstance(current_user.role, UserRole):
#         try:
#             current_user.role = UserRole(current_user.role)  # Convert to Enum if necessary
#         except ValueError:
#             print("🚨 ERROR: Invalid role format in token or database!")
#             raise HTTPException(status_code=400, detail="Invalid role format in token.")

#     # 🚨 Deny access if the user is not a DRIVER
#     if current_user.role != UserRole.DRIVER:
#         print("❌ ACCESS DENIED: User is not a DRIVER!")
#         raise HTTPException(status_code=403, detail="Only drivers can perform this action")

#     print("✅ ACCESS GRANTED: User is a DRIVER")
#     return current_user


def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures that only users with the DRIVER role can proceed.
    """

    logger.info(f"🟡 Authenticated User: {current_user.username}, Role: {current_user.role}")

    # ✅ Ensure role is an ENUM (some databases may store ENUM as string)
    try:
        user_role = UserRole(current_user.role) if isinstance(current_user.role, str) else current_user.role
    except ValueError:
        logger.error("🚨 ERROR: Invalid role format in token or database!")
        raise HTTPException(status_code=400, detail="Invalid role format in token.")

    # 🚨 Deny access if the user is not a DRIVER
    if user_role != UserRole.DRIVER:
        logger.warning(f"❌ ACCESS DENIED: User {current_user.username} is not a DRIVER!")
        raise HTTPException(status_code=403, detail="Only drivers can perform this action")

    logger.info("✅ ACCESS GRANTED: User is a DRIVER")
    return current_user



def generate_verification_code(length=8) -> str:
    """
    Generate a secure 8-character alphanumeric verification code.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def verify_verification_code(stored_code, input_code):
    """Verify if the stored verification code matches the user input."""
    return stored_code == input_code