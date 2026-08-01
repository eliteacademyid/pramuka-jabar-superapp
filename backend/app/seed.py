import uuid
from datetime import date, timedelta

from app import auth, models
from app.database import SessionLocal

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"


def seed_default_admin():
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            # Create default admin with membership data
            db.add(
                models.User(
                    username=DEFAULT_ADMIN_USERNAME,
                    hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
                    nama_lengkap=DEFAULT_ADMIN_FULLNAME,
                    role="admin",
                    is_active=True,
                    verification_token=uuid.uuid4(),
                    nomor_anggota="001-ADM-2025",
                    golongan="Pembina",
                    kwartir="Kwarda Jawa Barat",
                    membership_status="active",
                    valid_until=date.today() + timedelta(days=365),
                )
            )
            db.commit()
        else:
            # Update existing users without verification_token
            users_without_token = (
                db.query(models.User)
                .filter(models.User.verification_token == None)
                .all()
            )
            
            for user in users_without_token:
                user.verification_token = uuid.uuid4()
                
                # Set default membership status if not set
                if not hasattr(user, 'membership_status') or user.membership_status is None:
                    user.membership_status = "active"
                
                # Set default valid_until if not set (1 year from now)
                if not hasattr(user, 'valid_until') or user.valid_until is None:
                    user.valid_until = date.today() + timedelta(days=365)
            
            if users_without_token:
                db.commit()
                print(f"Updated {len(users_without_token)} users with verification tokens")
    finally:
        db.close()

