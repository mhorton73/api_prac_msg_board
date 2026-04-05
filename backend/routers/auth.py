
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth.utils import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    decode_token
)
from ..database import SessionLocal
from ..models import User
from ..schemas import UserIn, RegisterResponse, LoginResponse


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

router = APIRouter(prefix="/auth", tags = ["auth"])
security = HTTPBearer()

# -------- Endpoints -------- 

@router.post("/register", status_code=201) 
def register(user: UserIn, session=Depends(get_session)):
    hashed = hash_password(user.password)

    db_user = User(username=user.username, password_hash=hashed)
    session.add(db_user)
    session.commit()

    return RegisterResponse(status ="user created", username = user.username)

@router.post("/login", status_code=200)
def login(user: UserIn, session=Depends(get_session)):
    db_user = session.query(User).filter_by(username=user.username).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": db_user.username, "id": db_user.id})
    refresh_token = create_refresh_token({"sub": db_user.username, "id": db_user.id})

    return LoginResponse(access_token= access_token, refresh_token = refresh_token)

@router.post("/refresh")
def refresh_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    ''' Issues a new access token by using the refresh token. '''

    current_user = decode_token(auth.credentials)
    access_token = create_access_token({"id": current_user.user_id, "sub": current_user.username})
    return {"access_token": access_token}


# -------- Admin/ debug endpoints --------

@router.get("/users")
async def get_users(session = Depends(get_session)):

    users = [
        {
            "id": user.id,
            "username": user.username
        }
        for user in session.query(User).all()
    ]

    total = len(users)

    return {"total": total, "users": users} 

@router.delete("/users")
async def delete_user(id: int, session = Depends(get_session)):

    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Message not found")

    deleted_user = user.username

    session.delete(user)
    session.commit()

    return {"status":"deleted", "user" : deleted_user} 