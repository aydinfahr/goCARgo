from sqlalchemy.orm import Session
from db.models import User
from schemas import UserCreate, UserUpdate
from utils.hashing import hash_password  # ✅ Şifreyi güvenli bir şekilde hashlemek için
from fastapi import HTTPException


def create_user(db: Session, user_data: UserCreate):
    """
    Creates a new user with a hashed password.

    Args:
        db (Session): The database session.
        user_data (UserCreate): User creation schema containing email, username, password, full_name, and role.

    Returns:
        User: The created user object.
    """
    # ✅ Check if email or username is already in use
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username is already registered.")

    # ✅ Hash the password before storing it in the database
    hashed_password = hash_password(user_data.password)

    # ✅ Create new user instance
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,  # "driver" | "passenger" | "admin"
        verified_email=False,  # Default False until email verification is done
        verified_id=False,  # Default False until ID verification is done
        profile_picture=user_data.profile_picture  # Optional profile picture URL
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def get_user_by_id(db: Session, user_id: int):
    """
    Fetches a user by their unique ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        User: The retrieved user object.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email(db: Session, email: str):
    """
    Fetches a user by their email.

    Args:
        db (Session): The database session.
        email (str): The email of the user.

    Returns:
        User: The retrieved user object.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(db: Session, user_id: int, user_update_data: UserUpdate):
    """
    Updates user information.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to be updated.
        user_update_data (UserUpdate): User update schema.

    Returns:
        User: The updated user object.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Check if new email or username is already taken
    if user_update_data.email and user_update_data.email != user.email:
        existing_email = db.query(User).filter(User.email == user_update_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email is already in use.")

    if user_update_data.username and user_update_data.username != user.username:
        existing_username = db.query(User).filter(User.username == user_update_data.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username is already in use.")

    for key, value in user_update_data.dict(exclude_unset=True).items():
        setattr(user, key, value)  # ✅ Update only provided fields

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    """
    Deletes a user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user to be deleted.

    Returns:
        dict: Confirmation message.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


def verify_user_email(db: Session, user_id: int):
    """
    Marks a user's email as verified.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        User: The updated user object.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.verified_email = True
    db.commit()
    db.refresh(user)
    return user


def verify_user_id(db: Session, user_id: int):
    """
    Marks a user's ID verification as completed.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        User: The updated user object.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.verified_id = True
    db.commit()
    db.refresh(user)
    return user
