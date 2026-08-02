from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

ROLES = ("admin", "staff")
STATUS_KEGIATAN = ("direncanakan", "berlangsung", "selesai", "dibatalkan")
ALLOWED_FILE_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Kegiatan(Base):
    __tablename__ = "kegiatan"

    id = Column(Integer, primary_key=True, index=True)
    nama_kegiatan = Column(String(255), nullable=False)
    deskripsi = Column(Text, nullable=True)
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_selesai = Column(Date, nullable=False)
    penanggung_jawab_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="direncanakan")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    penanggung_jawab = relationship("User", backref="kegiatan_list")
    dokumentasi = relationship(
        "DokumentasiKegiatan", back_populates="kegiatan", uselist=False
    )


class DokumentasiKegiatan(Base):
    __tablename__ = "dokumentasi_kegiatan"

    id = Column(Integer, primary_key=True, index=True)
    kegiatan_id = Column(Integer, ForeignKey("kegiatan.id"), nullable=False, unique=True)
    catatan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kegiatan = relationship("Kegiatan", back_populates="dokumentasi")
    files = relationship("FileDokumentasi", backref="dokumentasi", cascade="all, delete-orphan")


class FileDokumentasi(Base):
    __tablename__ = "file_dokumentasi"

    id = Column(Integer, primary_key=True, index=True)
    dokumentasi_id = Column(Integer, ForeignKey("dokumentasi_kegiatan.id"), nullable=False)
    nama_file = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    ukuran = Column(Integer, nullable=False)
    tipe_file = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
