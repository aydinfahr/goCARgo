

from typing import List
from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import db_user
from db.database import get_db
from schemas import UserBase, UserDisplay



router = APIRouter(
    prefix='/user',
    tags=['user']
)


# Create user
@router.post('/', response_model=UserDisplay)
def create_user(request: UserBase, db: Session=Depends(get_db)):
    return db_user.create_user(db, request)



# Read all users - Temporary!!
@router.get('/', response_model=List[UserDisplay])
def get_all_users(db: Session=Depends(get_db)):
    return db_user.get_all_users(db)

# Read one user
@router.get('/{id}', response_model=UserDisplay)
def get_user(id: int, db: Session=Depends(get_db)):
    return db_user.get_user(db, id)


# Update user
@router.post('/{id}/update')
def update_user(id: int, request: UserBase, db: Session=Depends(get_db)):
    return db_user.update_user(db, id, request)

# Delete user
@router.get('/delete/{id}') #or ('/{id}/delete')
def delete_user(id: int, db: Session=Depends(get_db)):
    return db_user.delete_user(db, id)



    
class BirModel(BaseModel):  # model ismi?
    email: str
    password: str

@router.post('/login')
def login(credentials: BirModel, email: str=Body(
        ..., description='Enter your email'
        ), 
    password: str=Body(
        ..., description='Enter your password'
        )
):
    return {'message': "Login failed"}

# from fastapi import FastAPI
# from pydantic import BaseModel,EmailStr, Field

# app = FastAPI()

# class Login(BaseModel):
#     email: EmailStr = Field(..., description="User email address")
#     password: str = Field(
#         ..., 
#         min_length=8, 
#         max_length=20, 
#         pattern=r"^[A-Za-z\d@$!%*?&]+$",
#         description="Password must be 8-20 characters long and contain only letters, numbers, and special characters (@$!%*?&)."
#     )


# @app.post("/login")
# def login(data: Login):
#     return {"message": "Validation successful!"}
    






