# # from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# # from sqlalchemy.orm import Session
# # from db.database import get_db
# # from db.models import Car, User
# # from schemas import CarCreate, CarDisplay, CarUpdate
# # from utils.auth import get_current_user
# # from typing import List
# # import os
# # import shutil

# # router = APIRouter(
# #     prefix="/cars",
# #     tags=["Cars"]
# # )

# # # 📌 Register a Car (Only for Drivers)
# # @router.post("/", response_model=CarDisplay)
# # def register_car(
# #     brand: str = Form(...),
# #     model: str = Form(...),
# #     color: str = Form(...),
# #     plate_number: str = Form(...),  # 🔹 Added license plate
# #     images: List[UploadFile] = File(None),  # Multiple file support
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user),
# # ):
# #     """
# #     Allows only **drivers** to register their cars.
# #     """
# #     # if current_user.role != "driver":
# #     #     raise HTTPException(status_code=403, detail="You are not authorized to add a car. Only 'driver' accounts can register cars.")

# #     if current_user.role not in ["driver", "admin"]:
# #         raise HTTPException(status_code=403, detail="Only 'driver' or 'admin' accounts can register cars.")


# #     # 📌 Save uploaded images
# #     image_paths = []
# #     if images:
# #         upload_dir = "uploads/cars"
# #         os.makedirs(upload_dir, exist_ok=True)

# #         for image in images:
# #             file_path = f"{upload_dir}/{current_user.id}_{image.filename}"
# #             with open(file_path, "wb") as buffer:
# #                 shutil.copyfileobj(image.file, buffer)
# #             image_paths.append(file_path)

# #     # 📌 Create and save new car
# #     new_car = Car(
# #         owner_id=current_user.id,
# #         brand=brand,
# #         model=model,
# #         color=color,
# #         plate_number=plate_number,
# #         car_images=",".join(image_paths) if image_paths else None
# #     )

# #     db.add(new_car)
# #     db.commit()
# #     db.refresh(new_car)

# #     return new_car

# # # 📌 Get All Cars (Admin Only)
# # @router.get("/admin/all", response_model=List[CarDisplay])
# # def get_all_cars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# #     """
# #     Retrieves all cars in the system (**Admin Only**).
# #     """
# #     if current_user.role != "admin":
# #         raise HTTPException(status_code=403, detail="Not authorized to view all cars.")
    
# #     cars = db.query(Car).all()
# #     return cars

# # # 📌 Get a User's Cars
# # @router.get("/{user_id}", response_model=List[CarDisplay])
# # def get_user_cars(user_id: int, db: Session = Depends(get_db)):
# #     """
# #     Retrieves all cars owned by a specific user.
# #     """
# #     cars = db.query(Car).filter(Car.owner_id == user_id).all()

# #     if not cars:
# #         raise HTTPException(status_code=404, detail="No cars found for this user.")

# #     return cars

# # # 📌 Get Car Details by ID
# # @router.get("/car/{car_id}", response_model=CarDisplay)
# # def get_car(car_id: int, db: Session = Depends(get_db)):
# #     """
# #     Retrieves a specific car by ID.
# #     """
# #     car = db.query(Car).filter(Car.id == car_id).first()
    
# #     if not car:
# #         raise HTTPException(status_code=404, detail="Car not found.")

# #     return car

# # # 📌 Update Car Details (Only Owner or Admin)
# # @router.put("/{car_id}", response_model=CarDisplay)
# # def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# #     """
# #     Allows the **owner or an admin** to update car details.
# #     """
# #     car = db.query(Car).filter(Car.id == car_id).first()
    
# #     if not car:
# #         raise HTTPException(status_code=404, detail="Car not found.")

# #     if current_user.id != car.owner_id and current_user.role != "admin":
# #         raise HTTPException(status_code=403, detail="You are not authorized to update this car.")

# #     # Update only provided fields
# #     if car_update.brand:
# #         car.brand = car_update.brand
# #     if car_update.model:
# #         car.model = car_update.model
# #     if car_update.color:
# #         car.color = car_update.color
# #     if car_update.plate_number:
# #         car.plate_number = car_update.plate_number

# #     db.commit()
# #     db.refresh(car)

# #     return car

# # # 📌 Upload Car Image (Only Owner or Admin)
# # @router.post("/{car_id}/upload-image")
# # def upload_car_image(car_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# #     """
# #     Allows **a driver or admin** to upload an image of their car.
# #     """
# #     car = db.query(Car).filter(Car.id == car_id).first()

# #     if not car:
# #         raise HTTPException(status_code=404, detail="Car not found.")

# #     if current_user.id != car.owner_id and current_user.role != "admin":
# #         raise HTTPException(status_code=403, detail="You are not authorized to upload an image for this car.")

# #     # Save the image
# #     upload_dir = "uploads/cars"
# #     os.makedirs(upload_dir, exist_ok=True)

# #     file_path = f"{upload_dir}/{car_id}_{file.filename}"
# #     with open(file_path, "wb") as buffer:
# #         shutil.copyfileobj(file.file, buffer)

# #     car.car_images = file_path  # Update the image field in the database
# #     db.commit()
# #     db.refresh(car)

# #     return {"message": "Car image uploaded successfully", "image_url": file_path}

# # # 📌 Delete Car (Only Owner or Admin)
# # @router.delete("/{car_id}")
# # def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# #     """
# #     Allows the **owner or an admin** to delete a car.
# #     """
# #     car = db.query(Car).filter(Car.id == car_id).first()
    
# #     if not car:
# #         raise HTTPException(status_code=404, detail="Car not found.")

# #     if current_user.id != car.owner_id and current_user.role != "admin":
# #         raise HTTPException(status_code=403, detail="You are not authorized to delete this car.")

# #     db.delete(car)
# #     db.commit()

# #     return {"message": "Car deleted successfully."}


# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# from db.database import get_db
# from db.models import Car, User, UserRole  # ✅ ENUM Kullanımı için güncellendi
# from schemas import CarCreate, CarDisplay, CarUpdate
# from utils.auth import get_current_user, get_current_driver 
# from typing import List
# import os
# import shutil

# router = APIRouter(
#     prefix="/cars",
#     tags=["Cars"]
# )

# # 📌 Register a Car (Only for Drivers)
# @router.post("/", response_model=CarDisplay)
# def register_car(
#     brand: str = Form(...),
#     model: str = Form(...),
#     color: str = Form(...),
#     plate_number: str = Form(...),  # 🔹 Added license plate
#     images: List[UploadFile] = File(None),  # Multiple file support
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     Allows only **drivers** to register their cars.
#     """
#     # ✅ ENUM KONTROLÜ DÜZELTİLDİ (HATA BURADAYDI)
#     print(f"🟡 DEBUG: current_user.role = {current_user.role}")  # ENUM nesnesi mi?
#     print(f"🟡 DEBUG: current_user.role.value = {current_user.role.value}")  # String değeri mi?

#     if current_user.role.value != "DRIVER":
#         print("❌ Access Denied: Role is not DRIVER")
#         raise HTTPException(status_code=403, detail="Only drivers can register cars.")

#     print("✅ Access Granted!")

#     # 📌 Save uploaded images
#     image_paths = []
#     if images:
#         upload_dir = "uploads/cars"
#         os.makedirs(upload_dir, exist_ok=True)

#         for image in images:
#             file_path = f"{upload_dir}/{current_user.id}_{image.filename}"
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(image.file, buffer)
#             image_paths.append(file_path)

#     # 📌 Create and save new car
#     new_car = Car(
#         owner_id=current_user.id,
#         brand=brand,
#         model=model,
#         color=color,
#         plate_number=plate_number,
#         car_images=",".join(image_paths) if image_paths else None
#     )

#     db.add(new_car)
#     db.commit()
#     db.refresh(new_car)

#     return new_car

# # 📌 Get All Cars (Admin Only)
# @router.get("/admin/all", response_model=List[CarDisplay])
# def get_all_cars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """
#     Retrieves all cars in the system (**Admin Only**).
#     """
#     if current_user.role.value != "ADMIN":
#         raise HTTPException(status_code=403, detail="Not authorized to view all cars.")
    
#     cars = db.query(Car).all()
#     return cars

# # 📌 Get a User's Cars
# @router.get("/{user_id}", response_model=List[CarDisplay])
# def get_user_cars(user_id: int, db: Session = Depends(get_db)):
#     """
#     Retrieves all cars owned by a specific user.
#     """
#     cars = db.query(Car).filter(Car.owner_id == user_id).all()

#     if not cars:
#         raise HTTPException(status_code=404, detail="No cars found for this user.")

#     return cars

# # 📌 Get Car Details by ID
# @router.get("/car/{car_id}", response_model=CarDisplay)
# def get_car(car_id: int, db: Session = Depends(get_db)):
#     """
#     Retrieves a specific car by ID.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()
    
#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     return car

# # 📌 Update Car Details (Only Owner or Admin)
# @router.put("/{car_id}", response_model=CarDisplay)
# def update_car(car_id: int, car_update: CarUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """
#     Allows the **owner or an admin** to update car details.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()
    
#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     if current_user.id != car.owner_id and current_user.role.value != "ADMIN":
#         raise HTTPException(status_code=403, detail="You are not authorized to update this car.")

#     # Update only provided fields
#     if car_update.brand:
#         car.brand = car_update.brand
#     if car_update.model:
#         car.model = car_update.model
#     if car_update.color:
#         car.color = car_update.color
#     if car_update.plate_number:
#         car.plate_number = car_update.plate_number

#     db.commit()
#     db.refresh(car)

#     return car

# # 📌 Upload Car Image (Only Owner or Admin)
# @router.post("/{car_id}/upload-image")
# def upload_car_image(car_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """
#     Allows **a driver or admin** to upload an image of their car.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()

#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     if current_user.id != car.owner_id and current_user.role.value != "ADMIN":
#         raise HTTPException(status_code=403, detail="You are not authorized to upload an image for this car.")

#     # Save the image
#     upload_dir = "uploads/cars"
#     os.makedirs(upload_dir, exist_ok=True)

#     file_path = f"{upload_dir}/{car_id}_{file.filename}"
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     car.car_images = file_path  # Update the image field in the database
#     db.commit()
#     db.refresh(car)

#     return {"message": "Car image uploaded successfully", "image_url": file_path}

# # 📌 Delete Car (Only Owner or Admin)
# @router.delete("/{car_id}")
# def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """
#     Allows the **owner or an admin** to delete a car.
#     """
#     car = db.query(Car).filter(Car.id == car_id).first()
    
#     if not car:
#         raise HTTPException(status_code=404, detail="Car not found.")

#     if current_user.id != car.owner_id and current_user.role.value != "ADMIN":
#         raise HTTPException(status_code=403, detail="You are not authorized to delete this car.")

#     db.delete(car)
#     db.commit()

#     return {"message": "Car deleted successfully."}


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Car, User
from db.enums import UserRole  # ✅ ENUM Kullanımı için düzeltildi
from schemas import CarCreate, CarDisplay, CarUpdate
from utils.auth import get_current_user, get_current_driver
from typing import List
import os
import shutil

router = APIRouter(
    prefix="/cars",
    tags=["Cars"]
)

# 📌 Sadece Sürücüler Araç Kaydedebilir
@router.post("/", response_model=CarDisplay)
def register_car(
    brand: str = Form(...),
    model: str = Form(...),
    color: str = Form(...),
    plate_number: str = Form(...),  # 🔹 Plaka numarası eklendi
    images: List[UploadFile] = File(None),  # Çoklu dosya desteği
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_driver),  # ✅ Sadece `DRIVER` kullanıcılar çağırabilir
):
    """
    **Sadece sürücüler araç kaydedebilir.**
    """
    # 📌 Fotoğrafları kaydet
    image_paths = []
    if images:
        upload_dir = "uploads/cars"
        os.makedirs(upload_dir, exist_ok=True)

        for image in images:
            file_path = f"{upload_dir}/{current_user.id}_{image.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_paths.append(file_path)

    # 📌 Yeni aracı kaydet
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

# 📌 Tüm Araçları Listele (Sadece Adminler)
@router.get("/admin/all", response_model=List[CarDisplay])
def get_all_cars(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **Admin kullanıcılar için tüm araçları listeler.**
    """
    if not isinstance(current_user.role, UserRole):
        current_user.role = UserRole(current_user.role)  # ✅ ENUM'a çevir

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view all cars.")
    
    return db.query(Car).all()

# 📌 Kullanıcının Araçlarını Getir
@router.get("/{user_id}", response_model=List[CarDisplay])
def get_user_cars(user_id: int, db: Session = Depends(get_db)):
    """
    **Belirli bir kullanıcının sahip olduğu araçları getirir.**
    """
    cars = db.query(Car).filter(Car.owner_id == user_id).all()
    if not cars:
        raise HTTPException(status_code=404, detail="No cars found for this user.")
    return cars

# 📌 Belirli Bir Aracı Getir
@router.get("/car/{car_id}", response_model=CarDisplay)
def get_car(car_id: int, db: Session = Depends(get_db)):
    """
    **Belirli bir aracı getirir.**
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")
    return car

# 📌 Araç Güncelleme (Sadece Sahip veya Admin)
@router.put("/{car_id}", response_model=CarDisplay)
def update_car(
    car_id: int, 
    car_update: CarUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    **Sadece araç sahibi veya admin tarafından güncellenebilir.**
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    if not isinstance(current_user.role, UserRole):
        current_user.role = UserRole(current_user.role)

    if current_user.id != car.owner_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to update this car.")

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

# 📌 Araç Fotoğrafı Yükle (Sadece Sahip veya Admin)
@router.post("/{car_id}/upload-image")
def upload_car_image(
    car_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    **Sadece araç sahibi veya admin tarafından araç fotoğrafı yüklenebilir.**
    """
    car = db.query(Car).filter(Car.id == car_id).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    if not isinstance(current_user.role, UserRole):
        current_user.role = UserRole(current_user.role)

    if current_user.id != car.owner_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to upload an image for this car.")

    upload_dir = "uploads/cars"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{car_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    car.car_images = file_path
    db.commit()
    db.refresh(car)

    return {"message": "Car image uploaded successfully", "image_url": file_path}

# 📌 Araç Silme (Sadece Sahip veya Admin)
@router.delete("/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    **Sadece araç sahibi veya admin tarafından araç silinebilir.**
    """
    car = db.query(Car).filter(Car.id == car_id).first()
    
    if not car:
        raise HTTPException(status_code=404, detail="Car not found.")

    if not isinstance(current_user.role, UserRole):
        current_user.role = UserRole(current_user.role)

    if current_user.id != car.owner_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this car.")

    db.delete(car)
    db.commit()
    return {"message": "Car deleted successfully."}
