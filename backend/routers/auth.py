
from fastapi import APIRouter, HTTPException, Depends

from backend.auth.utils import hash_password, verify_password, create_access_token
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

# -------- Endpoints -------- 

@router.post("/register", status_code=201) 
def register(user: UserIn, session=Depends(get_session)):
    print(f"Password length: {len(user.password)}")
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

    token = create_access_token({"sub": db_user.username, "id": db_user.id})

    return LoginResponse(access_token= token, token_type = "bearer")