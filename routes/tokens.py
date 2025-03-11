from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from schemas import UserDisplay, UserUpdate, UserDeleteResponse
from utils.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.notifications import send_email
import shutil
import os

router = APIRouter(
    prefix="/tokens",
    tags=["Login"]
)

# ----------------------- 📌 User Token (JWT Authentication) ----------------------- #
@router.post("/")
def token(
    username: str = Form(...), 
    password: str = Form(...), 
    db: Session = Depends(get_db)
):
    """
    **User logs in and receives a JWT token.**
    """
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(db_user.id)
    return {"access_token": access_token, "token_type": "bearer"}

