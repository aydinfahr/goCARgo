
# from fastapi import HTTPException, Response, status
# from sqlalchemy.orm.session import Session
# from sqlalchemy.sql.expression import collate
# from schemas import RideBase
# from db.models import Ride, User, Car
# from datetime import date, datetime, timezone
# from sqlalchemy import func
# from db.enums import RideStatus


# def create_ride(db: Session, request: RideBase):
#     departure_datetime = request.departure_time  # Get datetime directly

#     if departure_datetime.tzinfo is not None:  # Ensure consistency
#         departure_datetime = departure_datetime.astimezone(timezone.utc).replace(tzinfo=None)

#     if departure_datetime < datetime.now():  # Now both are naive
#         raise HTTPException(status_code=400, detail="Departure time cannot be in the past")

#     # ✅ Directly use `departure_time` instead of `get_departure_datetime()`
#     departure_datetime = request.departure_time

#     # ✅ Check if driver exists
#     driver = db.query(User).filter(User.id == request.driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

#     # ✅ Check if car exists
#     car = db.query(Car).filter(Car.id == request.car_id).first()
#     if not car:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found.")

#     # ✅ Ensure the car belongs to the driver
#     if car.owner_id != request.driver_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver.")

#     # ✅ Prevent duplicate rides with the same departure time
#     existing_ride = db.query(Ride).filter(
#         Ride.driver_id == request.driver_id,
#         Ride.departure_time == departure_datetime
#     ).first()
#     if existing_ride:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A ride with the same details already exists.")

#     # ✅ Prevent setting a past departure time
#     if departure_datetime < datetime.now():
#         raise HTTPException(status_code=400, detail="Departure time cannot be in the past.")

#     # ✅ Validate price per seat
#     if request.price_per_seat <= 0:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price per seat must be greater than zero.")

#     # ✅ Validate seat count
#     if request.total_seats < 1 or request.total_seats > 4:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total seats must be between 1 and 4.")

#     # ✅ Validate instant booking flag
#     if not isinstance(request.instant_booking, bool):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid value for instant_booking.")

#     # ✅ Create ride instance
#     ride_data = request.model_dump()  # Convert the Pydantic model to a dictionary
#     new_ride = Ride(**ride_data, available_seats=request.total_seats)

#     db.add(new_ride)
#     db.commit()
#     db.refresh(new_ride)

#     return new_ride


# def get_all_rides(db: Session, driver_id, ride_status):
#     current_time = datetime.now()
#     ride_query = db.query(Ride)
    
#     if driver_id:
#         driver = db.query(User).filter(User.id == driver_id).first()
#         if not driver:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
#         ride_query = ride_query.filter(Ride.driver_id == driver_id)

#     if ride_status == RideStatus.past:
#         ride_query = ride_query.filter(Ride.departure_time < current_time)
#     elif ride_status == RideStatus.upcoming:
#         ride_query = ride_query.filter(Ride.departure_time >= current_time)
    
#     rides = ride_query.all()

#     return rides  # Return all rides if no status is provided

# def search_rides(
#         db: Session, 
#         start_location : str,
#         end_location : str,       #? Buralarda Optional[str] = None gerekli mi
#         departure_date : date, 
#         number_of_seats : int, 
#         ):
#         #handle any exception
#     ridesQuery = db.query(Ride)
#     if start_location:
#         ridesQuery = ridesQuery.filter(collate(Ride.start_location, "NOCASE") == start_location)
#     if end_location:
#         ridesQuery = ridesQuery.filter(collate(Ride.end_location, "NOCASE") == end_location)
#     if departure_date:
#         ridesQuery = ridesQuery.filter(func.date(Ride.departure_time) == departure_date)
#     if number_of_seats:
#         ridesQuery = ridesQuery.filter(Ride.available_seats >= number_of_seats)
       
#     rides = ridesQuery.all()
#     return rides


# def get_ride(db: Session, ride_id:int):
#     #user kontrolu gerekli mi?
#     ride = db.query(Ride).filter(Ride.id == ride_id).first()
#     if not ride: 
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip with ID {ride_id} not found")
#     return ride 


# def update_ride(db: Session, ride_id: int, request: RideBase):
#     departure_datetime = request.get_departure_datetime()

#     ride = db.query(Ride).filter(Ride.id == ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found")
    
#     car = db.query(Car).filter(Car.id == request.car_id).first()
#     if not car:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
#     driver = db.query(User).filter(User.id == request.driver_id).first()  
#     if not driver:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
#     if ride.driver_id != request.driver_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ride does not belong to the driver")
#     if car.owner_id != request.driver_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver")

#     ride_data = request.model_dump()  # Convert the Pydantic model to a dictionary
#     ride_data.pop("date", None)  # Remove fields that are not present in the SQLAlchemy model
#     ride_data.pop("time", None)

#      # Güncellenmesi gereken alanları ride nesnesine aktar
#     for key, value in ride_data.items():
#         setattr(ride, key, value)

#     # departure_time ve available_seats'ı güncelle
#     ride.departure_time = departure_datetime
#     ride.available_seats = request.total_seats

#     db.commit()
#     db.refresh(ride)
#     return ride


# def delete_ride(db: Session, driver_id: int,  ride_id: int):
#     ride = db.query(Ride).filter(Ride.id == ride_id).first()
#     if not ride:
#         raise HTTPException(status_code=404, detail="Ride not found")
    
#     driver = db.query(User).filter(User.id == driver_id).first()
#     if not driver:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
#     if ride.driver_id != driver_id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ride does not belong to the driver")
    
#     db.delete(ride)
#     db.commit() 
#     return Response(status_code=status.HTTP_204_NO_CONTENT)



from fastapi import HTTPException, Response, status
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import collate
from schemas import RideBase
from db.models import Ride, User, Car
from datetime import date, datetime, timezone
from sqlalchemy import func
from db.enums import RideStatus


def create_ride(db: Session, request: RideBase):
    """
    Creates a new ride in the system.
    - Checks for valid user, car, and duplicate ride.
    - Ensures the departure time is in the future.
    """

    departure_datetime = request.departure_time

    # ✅ Ensure departure_datetime is naive for proper comparison
    if departure_datetime.tzinfo is not None:
        departure_datetime = departure_datetime.astimezone(timezone.utc).replace(tzinfo=None)

    if departure_datetime < datetime.now():
        raise HTTPException(status_code=400, detail="Departure time cannot be in the past")

    # ✅ Validate driver
    driver = db.query(User).filter(User.id == request.driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    # ✅ Validate car
    car = db.query(Car).filter(Car.id == request.car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found.")

    # ✅ Ensure the car belongs to the driver
    if car.owner_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver.")

    # ✅ Prevent duplicate rides
    existing_ride = db.query(Ride).filter(
        Ride.driver_id == request.driver_id,
        Ride.departure_time == departure_datetime
    ).first()
    if existing_ride:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A ride with the same details already exists.")

    # ✅ Validate ride constraints
    if request.price_per_seat <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Price per seat must be greater than zero.")
    if request.total_seats < 1 or request.total_seats > 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Total seats must be between 1 and 4.")
    if not isinstance(request.instant_booking, bool):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid value for instant_booking.")

    # ✅ Create ride
    ride_data = request.model_dump()
    new_ride = Ride(**ride_data, available_seats=request.total_seats)

    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)

    return new_ride


def get_all_rides(db: Session, driver_id=None, ride_status=None):
    """
    Fetch all rides based on optional filters.
    - Filters by driver ID or ride status (past/upcoming).
    """

    current_time = datetime.now()
    ride_query = db.query(Ride)

    if driver_id:
        driver = db.query(User).filter(User.id == driver_id).first()
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
        ride_query = ride_query.filter(Ride.driver_id == driver_id)

    if ride_status == RideStatus.past:
        ride_query = ride_query.filter(Ride.departure_time < current_time)
    elif ride_status == RideStatus.upcoming:
        ride_query = ride_query.filter(Ride.departure_time >= current_time)

    return ride_query.all()


def search_rides(db: Session, start_location: str, end_location: str, departure_date: date, number_of_seats: int):
    """
    Searches for available rides based on location, date, and seats.
    """

    ridesQuery = db.query(Ride)

    if start_location:
        ridesQuery = ridesQuery.filter(collate(Ride.start_location, "NOCASE") == start_location)
    if end_location:
        ridesQuery = ridesQuery.filter(collate(Ride.end_location, "NOCASE") == end_location)
    if departure_date:
        ridesQuery = ridesQuery.filter(func.date(Ride.departure_time) == departure_date)
    if number_of_seats:
        ridesQuery = ridesQuery.filter(Ride.available_seats >= number_of_seats)

    return ridesQuery.all()


def get_ride(db: Session, ride_id: int):
    """
    Fetch a specific ride by its ID.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trip with ID {ride_id} not found.")
    return ride


def update_ride(db: Session, ride_id: int, request: RideBase):
    """
    Updates an existing ride while checking for ownership and constraints.
    """

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    # ✅ Validate car and driver
    car = db.query(Car).filter(Car.id == request.car_id).first()
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found.")
    
    driver = db.query(User).filter(User.id == request.driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")

    if ride.driver_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ride does not belong to the driver.")
    if car.owner_id != request.driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This car does not belong to the driver.")

    # ✅ Convert RideBase to dictionary
    ride_data = request.model_dump()
    ride_data.pop("date", None)  # Remove unnecessary fields
    ride_data.pop("time", None)

    # ✅ Apply updates
    for key, value in ride_data.items():
        setattr(ride, key, value)

    db.commit()
    db.refresh(ride)
    return ride


def delete_ride(db: Session, driver_id: int, ride_id: int):
    """
    Deletes a ride only if the requesting driver owns it.
    """

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    driver = db.query(User).filter(User.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found.")
    
    if ride.driver_id != driver_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This ride does not belong to the driver.")

    db.delete(ride)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
