
from fastapi import HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta

from backend.config import settings
from ..schemas import CurrentUser, MessageOut
from ..models import RefreshToken, Message, Tag

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
SESSION_LENGTH = settings.SESSION_LENGTH
REFRESH_TOKEN_LENGTH = settings.REFRESH_TOKEN_LENGTH

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=SESSION_LENGTH)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_LENGTH)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = RefreshToken(
        token = token,
        user_id = data["id"],
        expires_at = expire
    )
    return refresh_token

def remove_expired_tokens(session):
    now = datetime.now(timezone.utc)
    session.query(RefreshToken).filter(RefreshToken.expires_at <= now).delete()

def decode_token(token:str):
    """
    Decode a JWT and return a dictionary with user info.
    Raises HTTPException(401) if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return CurrentUser(id=user_id, username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")