
import sys
import os
from dotenv import load_dotenv
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

#  Ensure project root is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#  Load environment variables (.env)
load_dotenv()

# ????????
#  Retrieve environment variables (Ensure they are set)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

#  Ensure required environment variables are set
missing_env_vars = []
if not TWILIO_ACCOUNT_SID: missing_env_vars.append("TWILIO_ACCOUNT_SID")
if not TWILIO_AUTH_TOKEN: missing_env_vars.append("TWILIO_AUTH_TOKEN")
if not SENDGRID_API_KEY: missing_env_vars.append("SENDGRID_API_KEY")
if not SENDER_EMAIL: missing_env_vars.append("SENDER_EMAIL")

if missing_env_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_env_vars)}")

#  Database Imports
from db import models
from db.database import engine, Base

#  Initialize database (Ensure tables exist before the app starts)
Base.metadata.create_all(engine)

#  FastAPI application setup
app = FastAPI(
    title="goCARgo API",
    description="A professional car-sharing & ride-booking API GoCarGo.",
    version="1.0.0"
)

#  CORS Middleware (Allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔹 Replace with actual frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  Import & Include Routes (Ensure no duplicate imports)
from routes import authentication, user, car, ride, booking, review, payment
from utils.notifications import send_email, send_system_notifications

app.include_router(authentication.router)
app.include_router(user.router)  # User management
app.include_router(car.router)  # Car management
app.include_router(ride.router)  # Ride management
app.include_router(booking.router)  # Booking & payments
app.include_router(review.router)  # Reviews & ratings
app.include_router(payment.router)  # Payment processing

#  Health Check Endpoint
@app.get("/health", tags=["System"])
def health_check():
    """
     Simple health-check endpoint to verify if the API is running.
    """
    return {"status": "ok", "message": "API is running smoothly"}

#  Send Notifications in Background
@app.post("/send_notifications")
def send_notifications(background_tasks: BackgroundTasks):
    """
     Triggers background email & SMS notifications for users.
    """
    background_tasks.add_task(send_system_notifications)
    return {"message": "Notifications are being processed in the background"}

#  Run Application
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
