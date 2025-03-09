# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# from db.database import get_db
# from db.models import Car, User
# from schemas import CarCreate, CarDisplay, CarUpdate
# from utils.auth import get_current_user
# from typing import List
# import os
# import shutil

# router = APIRouter(
#     prefix="/cars",
#     tags=["Cars"]
# )

# # 📌 Araç Kaydı (Sadece Sürücüler İçin)

# # ✅ Sadece "driver" olan kullanıcılar araç ekleyebilir
# @router.post("/", response_model=CarDisplay)
# def register_car(
#     brand: str = Form(...),
#     model: str = Form(...),
#     color: str = Form(...),
#     images: list[UploadFile] = File(None),  # Birden fazla dosya desteği
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Allows only **drivers** to register their cars.
#     """
#     # 📌 Eğer kullanıcı "driver" değilse hata döndür
#     if current_user.role != "driver":
#         raise HTTPException(status_code=403, detail="Araç ekleme izniniz yok. Sadece 'driver' hesabı ile araç eklenebilir.")

#     # 📌 Resimleri kaydet ve yollarını listeye ekle
#     image_paths = []
#     if images:
#         upload_dir = "uploads/cars"
#         os.makedirs(upload_dir, exist_ok=True)

#         for image in images:
#             file_path = f"{upload_dir}/{current_user.id}_{image.filename}"
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(image.file, buffer)
#             image_paths.append(file_path)  # Kaydedilen dosyanın yolunu ekliyoruz

#     # 📌 Yeni araç ekleme
#     new_car = Car(
#         owner_id=current_user.id,
#         brand=brand,
#         model=model,
#         color=color,
#         car_images=",".join(image_paths) if image_paths else None  # Resimleri virgülle birleştiriyoruz
#     )

#     db.add(new_car)
#     db.commit()
#     db.refresh(new_car)

#     return new_car
# # 📌 Tüm Araçları Listeleme (Sadece Admin)
# @router.get("/admin/all", response_model=List[CarDisplay])
# def get_all_cars(db: Session = Depends(get_db)):
#     """
#     Retrieves all cars in the system (Admin only).
#     """
#     cars = db.query(Car).all()
#     return cars

# # 📌 Kullanıcının Araçlarını Listeleme
# @router.get("/{user_id}", response_model=List[CarDisplay])
# def get_user_cars(user_id: int, db: Session = Depends(get_db)):
#     """
#     Retrieves all cars owned by a specific user.
#     """
#     cars = db.query(Car).filter(Car.owner_id == user_id).all()

#     if not cars:
#         raise HTTPException(status_code=404, detail="No cars found for this user.")

#     return cars

# # 📌 Belirli bir Aracı Görüntüleme
# @router.get("/car/{car_id}", response_model=CarDisplay)
# def get_car(car_id: int, db: Session = Depends(get_db)):
#     """
#     Retrieves a specific car by ID.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()
    
#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     return car

# # 📌 Araç Bilgilerini Güncelleme (Sadece Sahibi veya Admin)
# @router.put("/{car_id}", response_model=CarDisplay)
# def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db)):
#     """
#     Allows the owner or an admin to update car details.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()
    
#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     # Güncellenmesi istenen alanlar varsa değiştirilir
#     car.brand = car_update.brand or car.brand
#     car.model = car_update.model or car.model
#     car.color = car_update.color or car.color
#     car.plate_number = car_update.plate_number or car.plate_number

#     db.commit()
#     db.refresh(car)

#     return car

# # 📌 Araç Resmi Yükleme (Opsiyonel)
# @router.post("/{car_id}/upload-image")
# def upload_car_image(car_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
#     """
#     Allows a driver to upload an image of their car.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()

#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     # Resim yükleme işlemi (örnek olarak dosya yolu kaydediliyor)
#     car.image_url = f"/images/{file.filename}"

#     db.commit()
#     db.refresh(car)

#     return {"message": "Car image uploaded successfully", "image_url": car.image_url}

# # 📌 Araç Silme (Sadece Sahibi veya Admin)
# @router.delete("/{car_id}")
# def delete_car(car_id: int, db: Session = Depends(get_db)):
#     """
#     Allows a driver or admin to delete a car.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()
    
#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     db.delete(car)
#     db.commit()

#     return {"message": "Car deleted successfully."}


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Car, User
from schemas import CarCreate, CarDisplay, CarUpdate
from utils.auth import get_current_user
from typing import List
import os
import shutil

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)

# 📌 Register a Car (Only for Drivers)
@router.post("/", response_model=CarDisplay)
def register_car(
    brand: str = Form(...),
    model: str = Form(...),
    color: str = Form(...),
    plate_number: str = Form(...),  # 🔹 Added license plate
    images: List[UploadFile] = File(None),  # Multiple file support
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Allows only **drivers** to register their cars.
    """
    if current_user.role != "driver":
        raise HTTPException(status_code=403, detail="You are not authorized to add a car. Only 'driver' accounts can register cars.")

    # 📌 Save uploaded images
    image_paths = []
    if images:
        upload_dir = "uploads/cars"
        os.makedirs(upload_dir, exist_ok=True)

        for image in images:
            file_path = f"{upload_dir}/{current_user.id}_{image.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_paths.append(file_path)

    # 📌 Create and save new car
    new_car = Car(
        owner_id=current_user.id,
        brand=brand,
        model=model,
        color=color,
        plate_number=plate_number,
        car_images=",".join(image_paths) if image_paths else None
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)

    return new_car

# 📌 Get All Cars (Admin Only)
@router.get("/admin/all", response_model=List[CarDisplay])
def get_all_cars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves all cars in the system (**Admin Only**).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view all cars.")
    
    cars = db.query(Car).all()
    return cars

# 📌 Get a User's Cars
@router.get("/{user_id}", response_model=List[CarDisplay])
def get_user_cars(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all cars owned by a specific user.
    """
    cars = db.query(Car).filter(Car.owner_id == user_id).all()

    if not cars:
        raise HTTPException(status_code=404, detail="No cars found for this user.")

    return cars

# 📌 Get Car Details by ID
@router.get("/car/{car_id}", response_model=CarDisplay)
def get_car(car_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a specific car by ID.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    return car

# 📌 Update Car Details (Only Owner or Admin)
@router.put("/{car_id}", response_model=CarDisplay)
def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows the **owner or an admin** to update car details.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    if current_user.id != car.owner_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to update this car.")

    # Update only provided fields
    if car_update.brand:
        car.brand = car_update.brand
    if car_update.model:
        car.model = car_update.model
    if car_update.color:
        car.color = car_update.color
    if car_update.plate_number:
        car.plate_number = car_update.plate_number

    db.commit()
    db.refresh(car)

    return car

# 📌 Upload Car Image (Only Owner or Admin)
@router.post("/{car_id}/upload-image")
def upload_car_image(car_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows **a driver or admin** to upload an image of their car.
    """
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    if current_user.id != car.owner_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to upload an image for this car.")

    # Save the image
    upload_dir = "uploads/cars"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{car_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    car.car_images = file_path  # Update the image field in the database
    db.commit()
    db.refresh(car)

    return {"message": "Car image uploaded successfully", "image_url": file_path}

# 📌 Delete Car (Only Owner or Admin)
@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Allows the **owner or an admin** to delete a car.
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    if current_user.id != car.owner_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to delete this car.")

    db.delete(car)
    db.commit()

    return {"message": "Car deleted successfully."}
