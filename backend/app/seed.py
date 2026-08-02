from app import auth, models
from app.database import SessionLocal

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"


def seed_default_admin():
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            db.add(
                models.User(
                    username=DEFAULT_ADMIN_USERNAME,
                    hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
                    nama_lengkap=DEFAULT_ADMIN_FULLNAME,
                    role="superadmin",
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()
