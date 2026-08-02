from datetime import datetime, date
from sqlalchemy import (
    Boolean, Column, DateTime, Date, Integer, String, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base

ROLES = ("admin", "staff", "member")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="member")
    nis = Column(String, nullable=True)
    kwaran = Column(String, nullable=True)
    kwarcab = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    level = Column(String(20), nullable=False)
    image_url = Column(String(255), nullable=True)
    requirements = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TKK(Base):
    __tablename__ = "tkk"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    bidang = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)
    image_url = Column(String(255), nullable=True)
    requirements = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    issuing_authority = Column(String(100), nullable=True)
    certificate_type = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)
    image_url = Column(String(255), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    achievement_type = Column(String(30), nullable=False)
    category = Column(String(50), nullable=True)
    level = Column(String(20), nullable=False)
    points = Column(Integer, default=0)
    image_url = Column(String(255), nullable=True)
    event_date = Column(Date, nullable=True)
    event_name = Column(String(100), nullable=True)
    organizer = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberAchievement(Base):
    __tablename__ = "member_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_type = Column(String(30), nullable=False)
    achievement_id = Column(Integer, nullable=False)
    earned_date = Column(Date, nullable=False)
    verified_by = Column(Integer, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="verified")
    notes = Column(Text, nullable=True)
    evidence_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
