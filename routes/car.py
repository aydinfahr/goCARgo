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
@router.post('/', response_model=CarDisplay)
def create_car(request: CarBase, db: Session=Depends(get_db)):
    return db_car.create_car(db, request)