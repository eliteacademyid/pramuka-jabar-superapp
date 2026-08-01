from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

ROLES = ("admin", "staff")
MEMBERSHIP_STATUS = ("active", "inactive", "expired", "pending")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Membership Card fields
    verification_token = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    nomor_anggota = Column(String, unique=True, index=True, nullable=True)
    golongan = Column(String, nullable=True)
    kwartir = Column(String, nullable=True)
    membership_status = Column(String, nullable=False, default="active")
    valid_until = Column(Date, nullable=True)
    foto_url = Column(String, nullable=True)
