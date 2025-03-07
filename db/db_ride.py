
from fastapi import HTTPException, Response, status
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import collate
from schemas import RideBase
from db.models import DbRide, DbUser, DbCar
from datetime import date, datetime
from sqlalchemy import func
from enums import RideStatus


def create_ride(db: Session, request: RideBase):
    departure_datetime = request.get_departure_datetime()

    driver = db.query(DbUser).filter(DbUser.id == request.driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

    car = db.query(DbCar).filter(DbCar.id == request.car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")

    if car.owner_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver")

    existing_ride = db.query(DbRide).filter(DbRide.driver_id == request.driver_id, DbRide.departure_time == departure_datetime).first()
    if existing_ride:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A ride with the same details already exists")

    if departure_datetime < datetime.now():
        raise HTTPException(status_code=400, detail="Departure time cannot be in the past")

    if request.price_per_seat <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price per seat must be greater than zero")

    if request.total_seats < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total seats must be at least 1")
    if request.total_seats > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total seats cannot be more than 4")
    
    ride_data = request.model_dump()  # Convert the Pydantic model to a dictionary
    ride_data.pop("date", None)  # Remove fields that are not present in the SQLAlchemy model
    ride_data.pop("time", None)

    new_ride = DbRide(**ride_data, departure_time=departure_datetime, available_seats=request.total_seats)

    #Alternative way to create new_ride
    # new_ride = DbRide(
    #     driver_id=request.driver_id,
    #     car_id=request.car_id,
    #     start_location=request.start_location,
    #     end_location=request.end_location,
    #     departure_time=departure_datetime,
    #     price_per_seat=request.price_per_seat,
    #     total_seats=request.total_seats,
    #     available_seats=request.total_seats
    # )
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    return new_ride


def get_all_rides(db: Session, driver_id, ride_status):
    current_time = datetime.now()
    ride_query = db.query(DbRide)
    
    if driver_id:
        ride_query = ride_query.filter(DbRide.driver_id == driver_id)

    if ride_status == RideStatus.past:
        ride_query = ride_query.filter(DbRide.departure_time < current_time)
    elif ride_status == RideStatus.upcoming:
        ride_query = ride_query.filter(DbRide.departure_time >= current_time)
    
    rides = ride_query.all()

    return rides  # Return all rides if no status is provided

def search_rides(
        db: Session, 
        start_location : str,
        end_location : str,       #? Buralarda Optional[str] = None gerekli mi
        departure_date : date, 
        number_of_seats : int, 
        ):
        #handle any exception
    ridesQuery = db.query(DbRide)
    if start_location:
        ridesQuery = ridesQuery.filter(collate(DbRide.start_location, "NOCASE") == start_location)
    if end_location:
        ridesQuery = ridesQuery.filter(collate(DbRide.end_location, "NOCASE") == end_location)
    if departure_date:
        ridesQuery = ridesQuery.filter(func.date(DbRide.departure_time) == departure_date)
    if number_of_seats:
        ridesQuery = ridesQuery.filter(DbRide.available_seats >= number_of_seats)
       
    rides = ridesQuery.all()
    return rides


def get_ride(db: Session, ride_id:int):
    #user kontrolu gerekli mi?
    ride = db.query(DbRide).filter(DbRide.id == ride_id).first()
    if not ride: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip with ID {ride_id} not found")
    return ride 


def update_ride(db: Session, ride_id: int, request: RideBase):
    departure_datetime = request.get_departure_datetime()

    ride = db.query(DbRide).filter(DbRide.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    car = db.query(DbCar).filter(DbCar.id == request.car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    driver = db.query(DbUser).filter(DbUser.id == request.driver_id).first()  
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    if ride.driver_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ride does not belong to the driver")
    if car.owner_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver")

    ride_data = request.model_dump()  # Convert the Pydantic model to a dictionary
    ride_data.pop("date", None)  # Remove fields that are not present in the SQLAlchemy model
    ride_data.pop("time", None)

     # Güncellenmesi gereken alanları ride nesnesine aktar
    for key, value in ride_data.items():
        setattr(ride, key, value)

    # departure_time ve available_seats'ı güncelle
    ride.departure_time = departure_datetime
    ride.available_seats = request.total_seats

    db.commit()
    db.refresh(ride)
    return ride


def delete_ride(db: Session, driver_id: int,  ride_id: int):
    ride = db.query(DbRide).filter(DbRide.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    driver = db.query(DbUser).filter(DbUser.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    if ride.driver_id != driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ride does not belong to the driver")
    
    db.delete(ride)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)

