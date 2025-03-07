from math import e
from fastapi import HTTPException, Response, status
from sqlalchemy.orm.session import Session
from schemas import CarBase
from db.models import DbCar, DbRide, DbUser


def create_car(db: Session, request: CarBase):
    owner = db.query(DbUser).filter(DbUser.id == request.owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_car = DbCar(
        owner_id = request.owner_id,
        brand = request.brand,
        model = request.model,
        color = request.color
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

def get_all_cars(db: Session, owner_id: int):
    owner = db.query(DbUser).filter(DbUser.id == owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if owner_id is None:
        return db.query(DbCar).all()  #Sadece admin bunu yapabilmeli
    else:    
        return db.query(DbCar).filter(DbCar.owner_id == owner_id).all()

def get_car_by_id(db: Session, car_id: int):
    car = db.query(DbCar).filter(DbCar.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return db.query(DbCar).filter(DbCar.id == car_id).first()

def update_car(db: Session, car_id: int, request: CarBase):
    owner = db.query(DbCar).filter(DbCar.owner_id == request.owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    car = db.query(DbCar).filter(DbCar.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if car.owner_id != request.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver")
    
    car.brand = request.brand
    car.model = request.model
    car.color = request.color
    # Alternative way to update car
    # update_data = request.model_dump()
    # update_data.pop("owner_id", None)  # owner_id cannot be updated
    # for key, value in update_data.items():
    #     setattr(car, key, value)  
    db.commit()
    db.refresh(car)
    return car

def delete_car(db: Session, car_id: int, owner_id: int):
    owner = db.query(DbUser).filter(DbUser.id == owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    car = db.query(DbCar).filter(DbCar.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found") 
    if car.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver") 

    ride_exists = db.query(DbRide).filter(DbRide.car_id == car_id).first()
    if ride_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This car has active or past rides. Please delete rides first."
        )
    db.delete(car)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
