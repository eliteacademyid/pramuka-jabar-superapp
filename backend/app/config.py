import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_cors_origins(raw: str) -> List[str]:
    """Parse comma-separated CORS origins dari environment variable."""
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class Settings:
    """Application configuration settings."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/db_pramuka_jabar",
    )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "super-apps-pramuka-jabar-secret-key-change-in-production",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS_ORIGINS dibaca dari env agar mudah dikonfigurasi per environment.
    # Contoh .env: CORS_ORIGINS=http://localhost:5173,https://app.pramuka-jabar.id
    CORS_ORIGINS: List[str] = _parse_cors_origins(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:8080",
        )
    )

    APP_NAME: str = "Super Apps Pramuka Jawa Barat"
    API_VERSION: str = "1.0.0"


settings = Settings()
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
DEBUG = settings.DEBUG
ENVIRONMENT = settings.ENVIRONMENT
