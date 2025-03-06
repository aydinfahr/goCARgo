from typing import List
from fastapi import FastAPI
from db import models
from db.database import engine
# import db.models  # Tüm modelleri yükle
import db.models  # Tüm modelleri bir defa yükle
db.models.DbReview


# Importing routers for different routes
from routes.user import router as user_router
from routes.car import router as car_router
from routes.ride import router as ride_router
from routes.booking import router as booking_router
from routes.review import router as review_router

app = FastAPI()

# Including routers in the FastAPI app
app.include_router(user_router)
app.include_router(car_router)
app.include_router(ride_router)
app.include_router(booking_router)
app.include_router(review_router)

# Creating database tables if they do not exist
models.Base.metadata.create_all(engine)

# git pull origin main 
# carsharing-venv\Scripts\activate 
# uvicorn main:app --reload



