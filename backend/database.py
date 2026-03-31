
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db_folder = "./backend/db"
os.makedirs(db_folder, exist_ok=True)

DATABASE_URL = "sqlite:///./backend/db/messages.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()