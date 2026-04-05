
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/db/messages.db")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    SESSION_LENGTH = int(os.getenv("SESSION_LENGTH", 1))
    REFRESH_TOKEN_LENGTH = int(os.getenv("REFRESH_TOKEN_LENGTH", 7))

settings = Settings()