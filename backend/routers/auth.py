
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.auth.utils import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    remove_expired_tokens,
    decode_token
)
from ..database import SessionLocal
from ..models import User, RefreshToken
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

    remove_expired_tokens(session)

    db_user = session.query(User).filter_by(username=user.username).first()

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    
    access_token = create_access_token({"sub": db_user.username, "id": db_user.id})
    refresh_token = create_refresh_token({"sub": db_user.username, "id": db_user.id})
    session.add(refresh_token)
    session.commit()

    return LoginResponse(access_token= access_token, refresh_token = refresh_token.token)

@router.post("/refresh")
def refresh_token(
    session=Depends(get_session), 
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    ''' Issues a new access token by using the refresh token. '''
    
    remove_expired_tokens(session)

    user = decode_token(auth.credentials)
    access_token = create_access_token({"id": user.id, "sub": user.username})
    refresh_token = create_refresh_token({"id": user.id, "sub": user.username})

    session.query(RefreshToken).filter_by(token=auth.credentials).delete()
    session.add(refresh_token)
    session.commit()

    return LoginResponse(access_token= access_token, refresh_token = refresh_token.token)

@router.post("/logout")
def logout(
    session=Depends(get_session), 
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    
    remove_expired_tokens(session)

    deleted = session.query(RefreshToken).filter_by(token=auth.credentials).delete()
    session.commit()

    if not deleted:
        raise HTTPException(status_code=404, detail="Token not found")

    return {"status": "logged out"}


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

@router.delete("/users/{id}")
async def delete_user(id: int, session = Depends(get_session)):

    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deleted_user = user.username

    session.delete(user)
    session.commit()

    return {"status":"deleted", "user" : deleted_user} 

@router.get("/tokens")
async def get_tokens(session = Depends(get_session)):

    tokens = [
        {
            "id": token.id,
            "user_id": token.user_id,
            "expires_at": token.expires_at
        }
        for token in session.query(RefreshToken).all()
    ]

    total = len(tokens)

    return {"total": total, "tokens": tokens} 

@router.delete("/tokens/{id}")
async def delete_token(session = Depends(get_session)):

    token = session.get(RefreshToken, id)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    deleted_token = token.id

    session.delete(token)
    session.commit()

    return {"status":"deleted", "token" : deleted_token} 
