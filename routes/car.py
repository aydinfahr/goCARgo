from typing import Optional
from requests import get
from sqlalchemy.orm import Session            
from fastapi import APIRouter, Depends, HTTPException
from db import db_car
from db.database import get_db
from db.models import User
from schemas import CarBase, CarDisplay
from utils.auth import get_current_user


from utils.auth import oauth2_scheme



router = APIRouter(
    prefix='/cars',
    tags=['Cars']
)

# Create car
@router.post('/', response_model=CarDisplay)
def create_car(request: CarBase, db: Session=Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.id != request.owner_id:
        raise HTTPException(status_code=403, detail="You are not authorized")

    return db_car.create_car(db, request)

# List User's Cars
@router.get("/", response_model=list[CarDisplay])
def get_all_cars(db: Session = Depends(get_db), owner_id: Optional[int]=None, current_user: User = Depends(get_current_user)):  #? db: Session = Depends(get_db)'i db_car'da mi tanimlasak
    if(current_user.is_admin):
        return db_car.get_all_cars(db, owner_id)
    
    if(owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    
    return db_car.get_all_cars(db, owner_id)

# Get Car Details
@router.get("/{id}", response_model=CarDisplay)
def get_car(id: int, db: Session = Depends(get_db)):
    return db_car.get_car_by_id(db, id)

# Update Car Details
@router.put("/{id}", response_model=CarDisplay) 
def update_car(id: int, request: CarBase, db: Session = Depends(get_db), owner_id: int=None, current_user: User=Depends(get_current_user)):
    if not current_user.is_admin and current_user.id != owner_id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    return db_car.update_car(db, id, request)

# Delete Car
@router.delete("/{id}")
def delete_car(id: int, db: Session = Depends(get_db), owner_id: int=None, current_user: User =Depends(get_current_user)):
    if not current_user.is_admin and current_user.id != owner_id:
        raise HTTPException(status_code=403, detail="You are not authorized")
    return db_car.delete_car(db, id, owner_id)
