from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base

ROLES = ("admin", "staff")


class RealisasiStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class LaporanStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


class ApprovalStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="role")


class Organisasi(Base):
    __tablename__ = "organisasi"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(150), unique=True, index=True, nullable=False)
    alamat = Column(String(255), nullable=True)
    telepon = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="organisasi")
    programs = relationship("Program", back_populates="organisasi")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String(100), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=2)
    organisasi_id = Column(Integer, ForeignKey("organisasi.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    organisasi = relationship("Organisasi", back_populates="users")
    programs = relationship("Program", back_populates="creator")
    realisasis = relationship("Realisasi", back_populates="creator")
    laporans = relationship("Laporan", back_populates="creator")
    approvals = relationship("Approval", back_populates="reviewer")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(150), index=True, nullable=False)
    deskripsi = Column(String, nullable=True)
    tahun = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organisasi_id = Column(Integer, ForeignKey("organisasi.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="programs")
    organisasi = relationship("Organisasi", back_populates="programs")
    kegiatans = relationship("Kegiatan", back_populates="program")
    realisasis = relationship("Realisasi", back_populates="program")


class Kegiatan(Base):
    __tablename__ = "kegiatans"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(150), index=True, nullable=False)
    deskripsi = Column(String, nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    tanggal_mulai = Column(DateTime, nullable=False)
    tanggal_selesai = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    lokasi = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    program = relationship("Program", back_populates="kegiatans")
    realisasis = relationship("Realisasi", back_populates="kegiatan")


class Realisasi(Base):
    __tablename__ = "realisasi"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(200), nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    target = Column(Integer, nullable=True)
    realisasi = Column(Integer, nullable=True)
    periode = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default=RealisasiStatus.draft.value, index=True)
    file_url = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    kegiatan_id = Column(Integer, ForeignKey("kegiatans.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="realisasis")
    program = relationship("Program", back_populates="realisasis")
    kegiatan = relationship("Kegiatan", back_populates="realisasis")
    documents = relationship("Dokumen", back_populates="realisasi")
    laporans = relationship("Laporan", back_populates="realisasi")


class Dokumen(Base):
    __tablename__ = "dokumen"

    id = Column(Integer, primary_key=True, index=True)
    nama_file = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    tipe = Column(String(100), nullable=True)
    ukuran = Column(Integer, nullable=True)
    realisasi_id = Column(Integer, ForeignKey("realisasi.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    realisasi = relationship("Realisasi", back_populates="documents")


class Laporan(Base):
    __tablename__ = "laporans"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(200), nullable=False, index=True)
    periode = Column(String(50), nullable=True)
    deskripsi = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=LaporanStatus.draft.value, index=True)
    realisasi_id = Column(Integer, ForeignKey("realisasi.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship("User", back_populates="laporans")
    realisasi = relationship("Realisasi", back_populates="laporans")
    approvals = relationship("Approval", back_populates="laporan")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    laporan_id = Column(Integer, ForeignKey("laporans.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default=ApprovalStatus.pending.value, index=True)
    catatan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    laporan = relationship("Laporan", back_populates="approvals")
    reviewer = relationship("User", back_populates="approvals")
