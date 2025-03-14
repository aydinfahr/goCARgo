from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm.session import Session
from db.models import User
from utils import hashing
from db.database import get_db
from utils import auth
from utils.email_service import send_verification_email


router = APIRouter(
    tags=['Authentication']
)

@router.post('/token')
def get_token(request: OAuth2PasswordRequestForm=Depends(), db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not hashing.verify_password(user.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = auth.create_access_token(data={'sub': user.username})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user_id': user.id,
        'user_name': user.username
    }



class EmailSchema(BaseModel):
    id: int

@router.post("/send-verification-email/", summary="Send Verification Email")
async def send_email(data: EmailSchema, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized to send verification email")
    
    user = db.query(User).filter(User.id == data.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Doğrulama bağlantısını oluştur
    verification_link = f"http://localhost:8000/verify-email?user_id={user.id}"

    # E-posta gönder
    send_verification_email(user.email, verification_link)

    return {"message": f"Verification email sent to {user.email}"}

# @router.post("/send-verification-email/")
# async def send_email(data: EmailSchema):
#     verification_link = f"http://localhost:8000/verify-email?email={data.email}"
#     send_verification_email(data.email, verification_link)
#     return {"message": "Verification email sent"}


@router.get("/verify-email/")
async def verify_email(user_id: int, db: Session = Depends(get_db)):
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Unauthorized to verify email")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.verified_email:
        return {"message": "User is already verified!"}

    # Kullanıcıyı doğrula
    user.verified_email = True
    db.commit()

    return {"message": "Email verification successful!"}
