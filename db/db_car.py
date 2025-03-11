from math import e
from fastapi import HTTPException, Response, status
from sqlalchemy.orm.session import Session
from schemas import CarBase
from db.models import Car, Ride, User


def create_car(db: Session, request: CarBase):
    owner = db.query(User).filter(User.id == request.owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_car = Car(
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
    car_query = db.query(Car)

    if owner_id:
        owner = db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        car_query = car_query.filter(Car.owner_id == owner_id).all()
    else:
        car_query =  car_query.all() #Sadece admin bunu yapabilmeli
        
    return car_query
      

def get_car_by_id(db: Session, car_id: int):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return db.query(Car).filter(Car.id == car_id).first()

def update_car(db: Session, car_id: int, request: CarBase):
    owner = db.query(Car).filter(Car.owner_id == request.owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    car = db.query(Car).filter(Car.id == car_id).first()
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
    owner = db.query(User).filter(User.id == owner_id).first()  
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found") 
    if car.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver") 

    ride_exists = db.query(Ride).filter(Ride.car_id == car_id).first()
    if ride_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This car has active or past rides. Please delete rides first."
        )
    db.delete(car)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
