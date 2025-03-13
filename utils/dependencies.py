from fastapi import Depends, HTTPException
from db.models import User
from utils.auth import verify_token  # ✅ Example dependency

def get_current_user(token: str = Depends(verify_token)) -> User:
    """
    Returns the current authenticated user based on the provided token.
    """
    user = verify_token(token)  # ✅ Verify token and get user
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
