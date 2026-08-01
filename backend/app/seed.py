from app import auth, models
from app.database import SessionLocal

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_EMAIL = "admin@pramuka.com"
DEFAULT_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_FULLNAME = "Administrator"


def seed_roles():
    """Create default roles"""
    db = SessionLocal()
    try:
        # Check if roles already exist
        if db.query(models.Role).count() == 0:
            roles = [
                models.Role(name="admin", description="Administrator role dengan akses penuh"),
                models.Role(name="staff", description="Staff role dengan akses terbatas"),
            ]
            db.add_all(roles)
            db.commit()
    finally:
        db.close()


def seed_default_admin():
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Seed roles first
        seed_roles()
        
        # Check if admin user exists
        if db.query(models.User).filter(models.User.username == DEFAULT_ADMIN_USERNAME).first():
            return
        
        # Get admin role
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        if not admin_role:
            seed_roles()
            admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        
        # Create admin user
        admin_user = models.User(
            username=DEFAULT_ADMIN_USERNAME,
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
            nama_lengkap=DEFAULT_ADMIN_FULLNAME,
            role_id=admin_role.id,
            is_active=True,
        )
        
        db.add(admin_user)
        db.commit()
        print("✓ Default admin user created successfully")
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding default admin: {e}")
    finally:
        db.close()
