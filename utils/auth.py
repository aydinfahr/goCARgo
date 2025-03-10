# # import os
# # from passlib.context import CryptContext
# # from datetime import datetime, timedelta
# # from typing import Optional
# # from jose import JWTError, jwt
# # from fastapi.security import OAuth2PasswordBearer
# # from fastapi import Depends, HTTPException, status
# # from sqlalchemy.orm import Session
# # from db.database import get_db
# # from db.models import User, UserRole
# # from dotenv import load_dotenv

# # # ✅ Load environment variables (.env)
# # load_dotenv()

# # # ✅ Password Hashing using Bcrypt
# # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # # ✅ JWT Token Configurations
# # SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # 📌 Must be set in .env
# # ALGORITHM = "HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# # # ✅ OAuth2 Scheme for Authentication
# # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# # # ------------------------ 🔐 Password Hashing Functions ------------------------ #

# # def hash_password(password: str) -> str:
# #     """
# #     Hashes a password securely using bcrypt.
# #     """
# #     return pwd_context.hash(password)

# # def verify_password(plain_password: str, hashed_password: str) -> bool:
# #     """
# #     Verifies the given password against the stored hashed password.
# #     """
# #     return pwd_context.verify(plain_password, hashed_password)

# # # ------------------------ 🔑 JWT Token Management ------------------------ #

# # def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
# #     """
# #     Creates a JWT access token for the given user ID and role.
# #     """
# #     to_encode = {"sub": str(user_id), "role": role}
# #     expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
# #     to_encode.update({"exp": expire})
    
# #     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# # def verify_token(token: str, credentials_exception, db: Session):
# #     """
# #     Decodes and verifies a JWT token, returning the authenticated user.
# #     """
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         user_id: str = payload.get("sub")
# #         user_role: str = payload.get("role")

# #         if user_id is None or user_role is None:
# #             raise credentials_exception
        
# #         # ✅ Fetch user from the database
# #         user = db.query(User).filter(User.id == int(user_id)).first()
# #         if user is None:
# #             raise credentials_exception
        
# #         return user
# #     except JWTError:
# #         raise credentials_exception

# # def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
# #     """
# #     Retrieves the current authenticated user from JWT token.
# #     """
# #     credentials_exception = HTTPException(
# #         status_code=status.HTTP_401_UNAUTHORIZED,
# #         detail="Could not validate credentials",
# #         headers={"WWW-Authenticate": "Bearer"},
# #     )
    
# #     return verify_token(token, credentials_exception, db)


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
# from db.enums import UserRole  # ✅ ENUM Kullanımı için ayrı dosyadan al
# from dotenv import load_dotenv

# # ✅ Ortam değişkenlerini yükle (.env dosyasından)
# load_dotenv()

# # ✅ Parola Hashleme (Bcrypt kullanarak güvenli şifreleme)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # ✅ JWT Token Konfigürasyonu
# SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # 📌 .env içinde olmalı!
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# # ✅ OAuth2 Şeması (JWT ile kimlik doğrulama)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# # ------------------------ 🔐 Parola İşlemleri ------------------------ #

# def hash_password(password: str) -> str:
#     """
#     Girilen parolayı bcrypt ile hashler.
#     """
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Girilen parolanın, hashlenmiş parola ile eşleşip eşleşmediğini kontrol eder.
#     """
#     return pwd_context.verify(plain_password, hashed_password)

# # ------------------------ 🔑 JWT Token Yönetimi ------------------------ #

# def create_access_token(user_id: int, role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Kullanıcı ID'si ve rolüne göre JWT erişim token'ı oluşturur.
#     """
#     payload = {"sub": str(user_id), "role": role.value}  # ✅ ENUM'un `.value` değerini saklıyoruz
#     expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     payload.update({"exp": expire})

#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# def verify_token(token: str, credentials_exception, db: Session):
#     """
#     JWT token'ı doğrular, çözer ve kullanıcıyı döndürür.
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("sub")
#         user_role: str = payload.get("role")

#         if not user_id or not user_role:
#             raise credentials_exception
        
#         # ✅ Kullanıcıyı veritabanında ara
#         user = db.query(User).filter(User.id == int(user_id)).first()
#         if not user:
#             raise credentials_exception

#         # ✅ ENUM olarak kullanıcı rolünü doğrula
#         try:
#             user.role = UserRole(user_role)  # ENUM formatına çevir
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid role in token.")

#         return user
#     except JWTError:
#         raise credentials_exception

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
#     """
#     JWT token kullanarak oturum açmış kullanıcıyı getirir.
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     user = verify_token(token, credentials_exception, db)

#     # ✅ Debugging - Hangi kullanıcının giriş yaptığını terminale yazdır
#     print(f"🟢 Authenticated User: {user.username}, Role: {user.role.value}")

#     return user

# def get_current_driver(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
#     """
#     **Sadece DRIVER rolüne sahip kullanıcıların giriş yapmasını sağlar.**
#     """
#     user = get_current_user(token, db)
    
#     if user.role != UserRole.DRIVER:  # ✅ ENUM Kullanımı
#         raise HTTPException(status_code=403, detail="Only drivers can perform this action")

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
from db.enums import UserRole  # ✅ ENUM Kullanımı için ayrı dosyadan al
from dotenv import load_dotenv

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
    JWT token'ı doğrular, çözer ve kullanıcıyı döndürür.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")

        if not user_id or not user_role:
            raise credentials_exception
        
        # ✅ Kullanıcıyı veritabanında ara
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise credentials_exception

        # ✅ ENUM formatında olduğundan emin ol
        try:
            user.role = UserRole(user_role)  # ENUM formatına çevir
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role in token.")

        return user
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    JWT token kullanarak oturum açmış kullanıcıyı getirir.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = verify_token(token, credentials_exception, db)

    # ✅ ENUM dönüşümünü garantile
    if not isinstance(user.role, UserRole):
        user.role = UserRole(user.role)  # ✅ ENUM'a çevir

    # ✅ Debugging - Hangi kullanıcının giriş yaptığını terminale yazdır
    print(f"🟢 Authenticated User: {user.username}, Role: {user.role.value}")

    return user

def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
    """
    **Sadece DRIVER rolüne sahip kullanıcıların giriş yapmasını sağlar.**
    """

    # 🟡 DEBUG: Kullanıcı bilgilerini logla
    print(f"🟡 DEBUG: Giriş yapan kullanıcı: {current_user.username}, Rol: {current_user.role}")

    # ✅ ENUM dönüşümünü doğrula (Bazı veritabanı sistemleri ENUM yerine string saklayabilir!)
    if isinstance(current_user.role, str):
        try:
            current_user.role = UserRole(current_user.role)  # Enum'a çevir
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role format in token.")

    # 🚨 Eğer kullanıcı DRIVER değilse, erişimi engelle
    if current_user.role != UserRole.DRIVER:
        print("❌ Erişim Engellendi: Kullanıcı DRIVER değil!")
        raise HTTPException(status_code=403, detail="Only drivers can perform this action")

    print("✅ Erişim İzin Verildi: Kullanıcı DRIVER")
    return current_user