from fastapi import FastAPI
from routes import booking, car, ride, user
from db import models
from db.database import engine


app = FastAPI()

app.include_router(user.router)
app.include_router(car.router)
app.include_router(ride.router)
app.include_router(booking.router)





models.Base.metadata.create_all(engine)