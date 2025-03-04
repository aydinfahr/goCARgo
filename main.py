from fastapi import FastAPI
from routes import booking, car, ride, user
from db import models
from db.database import engine
from routes import review

# git pull origin main 
# carsharing-env\Scripts\activate 
# uvicorn main:app --reload

app = FastAPI()

app.include_router(user.router)
app.include_router(car.router)
app.include_router(ride.router)
app.include_router(booking.router)
app.include_router(review.router)





models.Base.metadata.create_all(engine)