from sqlalchemy.orm import Session            


from fastapi import APIRouter, Depends

from db import db_car
from db.database import get_db
from schemas import CarBase, CarDisplay


router = APIRouter(
    prefix='/car',
    tags=['car']
)


# Create car
@router.post('/{owner_id}', response_model=CarDisplay)
def create_car(owner_id : int, request: CarBase, db: Session=Depends(get_db)):
    return db_car.create_car(owner_id, db, request)

# Get Car Details
@router.get("/{car_id}", response_model=CarDisplay)
def get_car(car_id: int, db: Session = Depends(get_db)):
    return db_car.get_car_by_id(db, car_id)

# List User's Cars
@router.get("/owner/{owner_id}", response_model=list[CarDisplay])
def get_user_cars(owner_id: int, db: Session = Depends(get_db)):
    return db_car.get_car(db, owner_id)

# Update Car Details
@router.put("/edit/{car_id}", response_model=CarDisplay)
def update_car(car_id: int, car_data: CarBase, db: Session = Depends(get_db)):
    return db_car.update_car(db,car_id, car_data)

# Delete Car
@router.delete("/{car_id}", response_model=CarDisplay)
def delete_car(car_id: int, db: Session = Depends(get_db)):
    return db_car.delete_car(db, car_id)
