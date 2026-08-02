import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres@localhost:5432/db_pramuka_jabar"
)
SECRET_KEY = os.getenv("SECRET_KEY", "super-apps-pramuka-jabar-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(Path(__file__).resolve().parent.parent / "uploads"))
