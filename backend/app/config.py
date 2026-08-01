import os
import secrets
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_cors_origins(raw: str) -> List[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


def _validate_secret_key(key: str) -> str:
    """Pastikan SECRET_KEY cukup kuat — minimal 32 karakter."""
    weak_defaults = {
        "super-apps-pramuka-jabar-secret-key-change-in-production",
        "secret",
        "changeme",
        "your-secret-key",
    }
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production" and (len(key) < 32 or key in weak_defaults):
        raise RuntimeError(
            "SECRET_KEY terlalu lemah untuk production. "
            "Gunakan string acak minimal 32 karakter. "
            f"Contoh: {secrets.token_hex(32)}"
        )
    return key


class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db" if ENVIRONMENT != "production" else "postgresql://postgres:postgres@localhost:5432/db_pramuka_jabar",
    )
    SECRET_KEY: str = _validate_secret_key(
        os.getenv("SECRET_KEY", "super-apps-pramuka-jabar-secret-key-change-in-production")
    )
    ALGORITHM: str = "HS256"
    # Turunkan dari 120 ke 60 menit — token lebih pendek = window serangan lebih kecil
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    CORS_ORIGINS: List[str] = _parse_cors_origins(
        os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8080",
        )
    )

    APP_NAME: str = "Super Apps Pramuka Jawa Barat"
    API_VERSION: str = "1.0.0"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
DEBUG = settings.DEBUG
ENVIRONMENT = settings.ENVIRONMENT
