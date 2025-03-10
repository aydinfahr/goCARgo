from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Car, User
from schemas import CarCreate, CarUpdate
from fastapi import HTTPException

def create_car(db: Session, car_data: CarCreate):
    """
    Creates a new car entry for a user.

    Args:
        db (Session): The database session.
        car_data (CarCreate): Car creation schema.

    Returns:
        Car: The created car object.
    """
    owner = db.query(User).filter(User.id == car_data.owner_id).first()

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found.")

    new_car = Car(
        owner_id=car_data.owner_id,
        brand=car_data.brand,
        model=car_data.model,
        color=car_data.color,
        license_plate=car_data.license_plate,
        car_photo=car_data.car_photo
    )

    db.add(new_car)

    try:
        db.commit()
        db.refresh(new_car)
        return new_car
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Car could not be created due to integrity constraints.")

def get_car_by_id(db: Session, car_id: int):
    """
    Fetches a car by its ID.

    Args:
        db (Session): The database session.
        car_id (int): The ID of the car.

    Returns:
        Car: The retrieved car object.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car

def get_cars_for_user(db: Session, user_id: int):
    """
    Retrieves all cars owned by a specific user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[Car]: List of cars for the user.
    """
    cars = db.query(Car).filter(Car.owner_id == user_id).all()

    if not cars:
        raise HTTPException(status_code=404, detail="No cars found for this user.")

    return cars

def update_car(db: Session, car_id: int, car_update_data: CarUpdate):
    """
    Updates a car's details.

    Args:
        db (Session): The database session.
        car_id (int): The ID of the car to be updated.
        car_update_data (CarUpdate): The updated car data.

    Returns:
        Car: The updated car object.
    """
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    for key, value in car_update_data.dict(exclude_unset=True).items():
        setattr(car, key, value)

    db.commit()
    db.refresh(car)
    
    return car

def delete_car(db: Session, car_id: int):
    """
    Deletes a car from the database.

    Args:
        db (Session): The database session.
        car_id (int): The ID of the car to be deleted.

    Returns:
        dict: Confirmation message.
    """
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    db.delete(car)
    db.commit()

    return {"message": "Car deleted successfully"}
