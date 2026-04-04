
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timezone, timedelta

SECRET_KEY = #censored
ALGORITHM = "HS256"
SESSION_LENGTH = 1

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    password = password[:72]
    password_bytes = password.encode("utf-8")
    print(f"Password in bytes: {password_bytes}")
    print(f"Length in bytes: {len(password_bytes)}")
    return pwd_context.hash(password_bytes)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=SESSION_LENGTH)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)