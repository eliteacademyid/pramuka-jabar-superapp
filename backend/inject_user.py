from app.database import SessionLocal
from app import models, auth

db = SessionLocal()
try:
    peserta = db.query(models.User).filter(models.User.username == "peserta1").first()
    if not peserta:
        db.add(
            models.User(
                username="peserta1",
                hashed_password=auth.hash_password("peserta123"),
                nama_lengkap="Peserta Dummy (Staff)",
                role="staff",
                is_active=True,
            )
        )
        db.commit()
        print("User peserta1 successfully injected!")
    else:
        print("User peserta1 already exists.")

    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin:
        print("Admin user not found.")
    else:
        print("Admin user exists.")
finally:
    db.close()
