from typing import Optional
from sqlalchemy.orm import Session            
from fastapi import APIRouter, Depends
from db import db_car
from db.database import get_db
from schemas import CarBase, CarDisplay


router = APIRouter(
    prefix='/cars',
    tags=['Cars']
)

# Create car
@router.post('/', response_model=CarDisplay)
def create_car(request: CarBase, db: Session=Depends(get_db)):
    return db_car.create_car(db, request)

# List User's Cars
@router.get("/", response_model=list[CarDisplay])
def get_all_cars(db: Session = Depends(get_db), owner_id: Optional[int]=None):  #? db: Session = Depends(get_db)'i db_car'da mi tanimlasak
    return db_car.get_all_cars(db, owner_id)

# Get Car Details
@router.get("/{id}", response_model=CarDisplay)
def get_car(id: int, db: Session = Depends(get_db)):
    return db_car.get_car_by_id(db, id)

# Update Car Details
@router.put("/{id}", response_model=CarDisplay) 
def update_car(id: int, request: CarBase, db: Session = Depends(get_db)):
    return db_car.update_car(db, id, request)

# Delete Car
@router.delete("/{id}")
def delete_car(id: int, db: Session = Depends(get_db), owner_id: int=None, ): #? Owner_id Query Param olarak mi alinmali?
    return db_car.delete_car(db, id, owner_id)
