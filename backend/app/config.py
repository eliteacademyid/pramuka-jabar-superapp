import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:syamstedc@localhost:5432/db_epelatihan"
)
SECRET_KEY = os.getenv("SECRET_KEY", "super-apps-pramuka-jabar-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
