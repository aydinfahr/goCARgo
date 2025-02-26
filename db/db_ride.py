from sqlalchemy.orm.session import Session
from schemas import RideBase
from db.models import DbBooking, DbRide
from datetime import date
from sqlalchemy import func

def create_ride(db: Session, request: RideBase):
    new_ride = DbRide(
        driver_id = request.driver_id,
        car_id = request.car_id,
        start_location = request.start_location,
        end_location = request.end_location,
        departure_time = request.departure_time, 
        price_per_seat = request.price_per_seat,
        available_seats = request.available_seats
    )
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    return new_ride

def get_ride(db: Session, id:int):
    #handle any exception
    return db.query(DbRide).filter(DbRide.id == id).first()
    

def search_ride(
        db: Session, 
        start_location : str,
        end_location : str,
        departure_date : date, 
        number_of_seats : int, 
        ):
        #handle any exception

    ridesQuery = db.query(DbRide)
    
    if start_location:
        ridesQuery = ridesQuery.filter(DbRide.start_location == start_location)
    
    if end_location:
        ridesQuery = ridesQuery.filter(DbRide.end_location == end_location)
    
    if departure_date:
        ridesQuery = ridesQuery.filter(func.date(DbRide.departure_time) == departure_date)
    
    if number_of_seats:
        ridesQuery = ridesQuery.filter(DbRide.total_seats >= number_of_seats)
       
    rides = ridesQuery.all()
    return rides

def calculate_available_seats(db:Session, ride: DbRide):
    booked_seats = db.query(DbBooking).filter(ride.id == DbBooking.ride_id).all()
    return ride.total_seats - sum(m.seats_booked for m in booked_seats)

