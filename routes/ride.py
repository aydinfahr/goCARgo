from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Ride, User
from schemas import RideCreate, RideDisplay, RideUpdate
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/rides",
    tags=["Rides"]
)

# 📌 Yolculuk oluşturma
@router.post("/", response_model=RideDisplay)
def create_ride(ride: RideCreate, db: Session = Depends(get_db)):
    """
    Allows drivers to create a new ride.
    """
    driver = db.query(User).filter(User.id == ride.driver_id, User.role == "driver").first()
    if not driver:
        raise HTTPException(status_code=403, detail="Only drivers can create rides.")

    new_ride = Ride(
        driver_id=ride.driver_id,
        car_id=ride.car_id,
        start_location=ride.start_location,
        end_location=ride.end_location,
        departure_time=ride.departure_time,
        price_per_seat=ride.price_per_seat,
        total_seats=ride.total_seats,
        status="active"
    )

    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    return new_ride

# 📌 Tüm rides listeleme (Filtreleme Seçenekleri ile)
@router.get("/", response_model=List[RideDisplay])
def get_rides(
    start_location: str = None,
    end_location: str = None,
    min_price: float = None,
    max_price: float = None,
    driver_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Retrieves available rides based on filters:
    - start_location, end_location, price range, driver_id
    """
    query = db.query(Ride).filter(Ride.status == "active")

    if start_location:
        query = query.filter(Ride.start_location.ilike(f"%{start_location}%"))
    if end_location:
        query = query.filter(Ride.end_location.ilike(f"%{end_location}%"))
    if min_price:
        query = query.filter(Ride.price_per_seat >= min_price)
    if max_price:
        query = query.filter(Ride.price_per_seat <= max_price)
    if driver_id:
        query = query.filter(Ride.driver_id == driver_id)

    rides = query.all()
    
    if not rides:
        raise HTTPException(status_code=404, detail="No rides found with given criteria.")

    return rides

# 📌 Belirli bir ride'ı görüntüleme
@router.get("/{ride_id}", response_model=RideDisplay)
def get_ride(ride_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific ride by ID.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")
    
    return ride

# 📌 Ride Güncelleme (Sadece Şoför veya Admin)
@router.put("/{ride_id}", response_model=RideDisplay)
def update_ride(ride_id: int, ride_update: RideUpdate, db: Session = Depends(get_db)):
    """
    Allows the driver or an admin to update ride details.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    # Güncellenmesi istenen alanlar varsa değiştirilir
    ride.start_location = ride_update.start_location or ride.start_location
    ride.end_location = ride_update.end_location or ride.end_location
    ride.departure_time = ride_update.departure_time or ride.departure_time
    ride.price_per_seat = ride_update.price_per_seat or ride.price_per_seat
    ride.total_seats = ride_update.total_seats or ride.total_seats
    ride.status = ride_update.status or ride.status  # active, completed, cancelled

    db.commit()
    db.refresh(ride)

    return ride

# 📌 Ride Silme (Sadece Şoför veya Admin)
@router.delete("/{ride_id}")
def delete_ride(ride_id: int, db: Session = Depends(get_db)):
    """
    Allows a driver or admin to delete a ride.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found.")

    db.delete(ride)
    db.commit()

    return {"message": "Ride deleted successfully."}

# 📌 Admin: Tüm Ride’ları Listeleme
@router.get("/admin/all")
def get_all_rides(db: Session = Depends(get_db)):
    """
    Retrieves all rides in the system (Admin only).
    """
    rides = db.query(Ride).all()
    return rides
