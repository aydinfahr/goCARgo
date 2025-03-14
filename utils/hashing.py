from passlib.context import CryptContext

# ✅ BCrypt ile şifreleme için yapılandırma
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes the password before storing it in the database."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies the provided password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

