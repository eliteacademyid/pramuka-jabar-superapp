from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)
with SessionLocal() as session:
    count = session.query(models.Role).count()
    print(f"roles-count={count}")
