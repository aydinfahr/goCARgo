
# from passlib.context import CryptContext

# from typing import Optional
# from jose import JWTError, jwt

# from fastapi import Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from db.database import get_db
# from db.models import User




import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import datetime,timezone, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session


from db.database import get_db
from db.models import User

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
 
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # Timezone-aware UTC datetime kullanımı
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    
    to_encode.update({"exp": expire})
    
    # JWT oluşturma
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str, credentials_exception, db: Session):
  
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if not username :
            raise credentials_exception
      
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise credentials_exception
        
        return user
    except JWTError:
        raise credentials_exception



def get_current_user(token: str=Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    user = verify_token(token, credentials_exception, db)

    return user








# # ✅ Ortam değişkenlerini yükle (.env dosyasından)
# load_dotenv()

# # ✅ Parola Hashleme (Bcrypt kullanarak güvenli şifreleme)
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # ✅ JWT Token Konfigürasyonu
# SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # 📌 .env içinde olmalı!
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))



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

# def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Kullanıcı ID'si ve rolüne göre JWT erişim token'ı oluşturur.
#     """
#     payload = {"sub": str(user_id)}  
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
        

#         if not user_id :
#             raise credentials_exception
        
#         # ✅ Kullanıcıyı veritabanında ara
#         user = db.query(User).filter(User.id == int(user_id)).first()
#         if not user:
#             raise credentials_exception

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

#     # ✅ ENUM dönüşümünü garantile
#     if not isinstance(user.role, UserRole):
#         user.role = UserRole(user.role)  # ✅ ENUM'a çevir

#     # ✅ Debugging - Hangi kullanıcının giriş yaptığını terminale yazdır
#     print(f"🟢 Authenticated User: {user.username}, Role: {user.role.value}")

#     return user

# def get_current_driver(current_user: User = Depends(get_current_user)) -> User:
#     """
#     **Sadece DRIVER rolüne sahip kullanıcıların giriş yapmasını sağlar.**
#     """

#     # 🟡 DEBUG: Kullanıcı bilgilerini logla
#     print(f"🟡 DEBUG: Giriş yapan kullanıcı: {current_user.username}, Rol: {current_user.role}")

#     # ✅ ENUM dönüşümünü doğrula (Bazı veritabanı sistemleri ENUM yerine string saklayabilir!)
#     if isinstance(current_user.role, str):
#         try:
#             current_user.role = UserRole(current_user.role)  # Enum'a çevir
#         except ValueError:
#             raise HTTPException(status_code=400, detail="Invalid role format in token.")

#     # 🚨 Eğer kullanıcı DRIVER değilse, erişimi engelle
#     if current_user.role != UserRole.DRIVER:
#         print("❌ Erişim Engellendi: Kullanıcı DRIVER değil!")
#         raise HTTPException(status_code=403, detail="Only drivers can perform this action")

#     print("✅ Erişim İzin Verildi: Kullanıcı DRIVER")
#     return current_user