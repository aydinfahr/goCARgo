# import os
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from fastapi.security import OAuth2PasswordBearer
# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from db.database import get_db
# from db.models import User
# from dotenv import load_dotenv

# # ✅ .env dosyasını yükleme (Gizli anahtarları yönetmek için)
# load_dotenv()

# # ✅ Şifreleme için Bcrypt ayarları
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # ✅ JWT için gerekli sabitler
# SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # 📌 Çevre değişkenlerinden alınmalı
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# # ✅ OAuth2 şeması (Token doğrulamak için kullanılır)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# # ------------------------ 🔐 Şifreleme Fonksiyonları ------------------------ #

# def hash_password(password: str) -> str:
#     """
#     Hashes a password securely using bcrypt.
#     """
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Verifies the given password against the stored hashed password.
#     """
#     return pwd_context.verify(plain_password, hashed_password)

# # ------------------------ 🔑 JWT Token Yönetimi ------------------------ #

# def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Creates a JWT access token with user ID and role.
#     """
#     to_encode = {"sub": str(user_id), "role": role}
#     expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
    
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def verify_token(token: str, credentials_exception):
#     """
#     Decodes and verifies a JWT token.
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("sub")
#         user_role: str = payload.get("role")

#         if user_id is None or user_role is None:
#             raise credentials_exception
        
#         return {"user_id": user_id, "role": user_role}
#     except JWTError:
#         raise credentials_exception

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     """
#     Retrieves the current authenticated user from JWT token.
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     user_data = verify_token(token, credentials_exception)
    
#     user = db.query(User).filter(User.id == user_data["user_id"]).first()
#     if user is None:
#         raise credentials_exception
    
#     return user


import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from dotenv import load_dotenv

# ✅ Load environment variables (.env)
load_dotenv()

# ✅ Password Hashing using Bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ JWT Token Configurations
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # 📌 Must be set in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# ✅ OAuth2 Scheme for Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# ------------------------ 🔐 Password Hashing Functions ------------------------ #

def hash_password(password: str) -> str:
    """
    Hashes a password securely using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies the given password against the stored hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

# ------------------------ 🔑 JWT Token Management ------------------------ #

def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token for the given user ID and role.
    """
    to_encode = {"sub": str(user_id), "role": role}
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, credentials_exception, db: Session):
    """
    Decodes and verifies a JWT token, returning the authenticated user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")

        if user_id is None or user_role is None:
            raise credentials_exception
        
        # ✅ Fetch user from the database
        user = db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
        
        return user
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieves the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    return verify_token(token, credentials_exception, db)
