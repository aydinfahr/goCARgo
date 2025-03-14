import argparse
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User
from passlib.context import CryptContext
import getpass

# Load environment variables from .env file
load_dotenv()

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hashes the given password using bcrypt."""
    return pwd_context.hash(password)

def create_initial_admin(password):
    """Creates the initial admin user with required fields."""
    db = SessionLocal()

    admin_email = os.getenv("ADMIN_EMAIL")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")  # Default username if not set
    admin_full_name = os.getenv("ADMIN_FULL_NAME", "Admin User")  # Default full name if not set

    if not admin_email:
        print(" ERROR: ADMIN_EMAIL is missing in the .env file!")
        return

    # Check if the admin user already exists
    existing_admin = db.query(User).filter_by(email=admin_email).first()

    if not existing_admin:
        hashed_password = get_password_hash(password)  # Hash the input password
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password=hashed_password,  # Store the hashed password
            full_name=admin_full_name,  # Provide full_name to avoid NULL errors
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin {admin_email} ({admin_username}) successfully created!")
    else:
        print("ℹAdmin already exists, no action taken.")

    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--password", help="Admin password (optional, will prompt if not provided)")
    args = parser.parse_args()

    # Secure password input if not provided in the command
    if not args.password:
        password = getpass.getpass("Enter admin password: ")  # Secure password input
    else:
        password = args.password

    create_initial_admin(password)
