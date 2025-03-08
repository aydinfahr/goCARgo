from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import Ride, User, Car
from schemas import RideCreate, RideUpdate
from fastapi import HTTPException
from datetime import datetime

def create_ride(db: Session, ride_data: RideCreate):
    """
    Creates a new ride in the database.

    Args:
        db (Session): The database session.
        ride_data (RideCreate): Ride creation schema.

    Returns:
        Ride: The created ride object.
    """
    driver = db.query(User).filter(User.id == ride_data.driver_id, User.role == "driver").first()
    car = db.query(Car).filter(Car.id == ride_data.car_id, Car.owner_id == ride_data.driver_id).first()

    if not driver:
        raise HTTPException(status_code=403, detail="Only registered drivers can create rides.")

    if not car:
        raise HTTPException(status_code=404, detail="Car not found or not owned by this driver.")

    new_ride = Ride(
        driver_id=ride_data.driver_id,
        car_id=ride_data.car_id,
        start_location=ride_data.start_location,
        end_location=ride_data.end_location,
        departure_time=ride_data.departure_time,
        price_per_seat=ride_data.price_per_seat,
        total_seats=ride_data.total_seats
    )

    db.add(new_ride)
    
    try:
        db.commit()
        db.refresh(new_ride)
        return new_ride
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ride could not be created due to integrity constraints.")

def get_ride_by_id(db: Session, ride_id: int):
    """
    Fetches a ride by its ID.

    Args:
        db (Session): The database session.
        ride_id (int): The ID of the ride.

    Returns:
        Ride: The retrieved ride object.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

def get_available_rides(db: Session, start_location: str = None, end_location: str = None):
    """
    Retrieves all available rides based on optional filters.

    Args:
        db (Session): The database session.
        start_location (str, optional): The start location filter.
        end_location (str, optional): The end location filter.

    Returns:
        List[Ride]: List of available rides.
    """
    query = db.query(Ride).filter(Ride.departure_time > datetime.utcnow())

    if start_location:
        query = query.filter(Ride.start_location.ilike(f"%{start_location}%"))
    if end_location:
        query = query.filter(Ride.end_location.ilike(f"%{end_location}%"))

    rides = query.all()

    if not rides:
        raise HTTPException(status_code=404, detail="No available rides found.")

    return rides

def update_ride(db: Session, ride_id: int, ride_update_data: RideUpdate):
    """
    Updates ride details.

    Args:
        db (Session): The database session.
        ride_id (int): The ID of the ride to be updated.
        ride_update_data (RideUpdate): The updated ride data.

    Returns:
        Ride: The updated ride object.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    for key, value in ride_update_data.dict(exclude_unset=True).items():
        setattr(ride, key, value)

    db.commit()
    db.refresh(ride)
    
    return ride

def delete_ride(db: Session, ride_id: int):
    """
    Deletes a ride from the database.

    Args:
        db (Session): The database session.
        ride_id (int): The ID of the ride to be deleted.

    Returns:
        dict: Confirmation message.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    db.delete(ride)
    db.commit()
    
    return {"message": "Ride deleted successfully"}
