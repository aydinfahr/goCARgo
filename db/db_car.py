from fastapi import HTTPException
from sqlalchemy.orm.session import Session
from schemas import CarBase
from db.models import DbCar

def create_car(owner_id: int, db: Session, request: CarBase):
    new_car = DbCar(
        owner_id = owner_id,
        brand = request.brand,
        model = request.model,
        color = request.color
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

def get_car(db: Session, owner_id: int):
    return db.query(DbCar).filter(DbCar.owner_id == owner_id).all()

def get_car_by_id(db: Session, car_id: int):
    return db.query(DbCar).filter(DbCar.id == car_id).first()

def update_car(db: Session, car_id: int, request: CarBase):
    car = db.query(DbCar).filter(DbCar.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for key, value in request.model_dump().items():
        setattr(car, key, value)

    db.commit()
    db.refresh(car)
    return car

def delete_car(db: Session, car_id: int):
    car = db.query(DbCar).filter(DbCar.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")    
    db.delete(car)
    db.commit()
    return car