from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text
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
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
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
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, default=2, index=True)
    organisasi_id = Column(Integer, ForeignKey("organisasi.id"), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    organisasi = relationship("Organisasi", back_populates="users")
    programs = relationship("Program", back_populates="creator")
    realisasis = relationship("Realisasi", back_populates="creator")
    laporans = relationship(
        "Laporan",
        back_populates="creator",
        primaryjoin="User.id == Laporan.created_by_id",
    )
    reviewed_laporans = relationship(
        "Laporan",
        back_populates="reviewer",
        primaryjoin="User.id == Laporan.approved_by_id",
    )
    approvals = relationship("Approval", back_populates="reviewer")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(150), index=True, nullable=False)
    deskripsi = Column(String, nullable=True)
    tahun = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    organisasi_id = Column(Integer, ForeignKey("organisasi.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index: filter tahun + status (pola paling umum di list programs)
    __table_args__ = (
        Index("ix_programs_tahun_status", "tahun", "status"),
        Index("ix_programs_organisasi_status", "organisasi_id", "status"),
    )

    creator = relationship("User", back_populates="programs")
    organisasi = relationship("Organisasi", back_populates="programs")
    kegiatans = relationship("Kegiatan", back_populates="program")
    realisasis = relationship("Realisasi", back_populates="program")


class Kegiatan(Base):
    __tablename__ = "kegiatans"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(150), index=True, nullable=False)
    deskripsi = Column(String, nullable=True)
    # index=True pada FK agar JOIN dan filter by program_id cepat
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    tanggal_mulai = Column(DateTime, nullable=False, index=True)
    tanggal_selesai = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    lokasi = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index untuk pola filter yang paling umum: program + status
    __table_args__ = (
        Index("ix_kegiatans_program_status", "program_id", "status"),
    )

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
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True, index=True)
    kegiatan_id = Column(Integer, ForeignKey("kegiatans.id"), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index untuk filter + sort yang paling umum
    __table_args__ = (
        Index("ix_realisasi_status_created", "status", "created_at"),
        Index("ix_realisasi_created_by_status", "created_by_id", "status"),
    )

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
    # index=True agar selectinload Dokumen by realisasi_id cepat
    realisasi_id = Column(Integer, ForeignKey("realisasi.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    realisasi = relationship("Realisasi", back_populates="documents")


class Laporan(Base):
    __tablename__ = "laporans"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String(200), nullable=False, index=True)
    periode = Column(String(50), nullable=True)
    deskripsi = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=LaporanStatus.draft.value, index=True)
    deadline = Column(DateTime, nullable=True, index=True)
    realisasi_id = Column(Integer, ForeignKey("realisasi.id"), nullable=True, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index untuk filter by status + sort by created_at (pola paling umum)
    __table_args__ = (
        Index("ix_laporans_status_created", "status", "created_at"),
    )

    creator = relationship(
        "User",
        back_populates="laporans",
        primaryjoin="Laporan.created_by_id == User.id",
    )
    reviewer = relationship(
        "User",
        back_populates="reviewed_laporans",
        primaryjoin="Laporan.approved_by_id == User.id",
    )
    realisasi = relationship("Realisasi", back_populates="laporans")
    approvals = relationship("Approval", back_populates="laporan")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    # index=True agar query by laporan_id cepat
    laporan_id = Column(Integer, ForeignKey("laporans.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=ApprovalStatus.pending.value, index=True)
    catatan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    laporan = relationship("Laporan", back_populates="approvals")
    reviewer = relationship("User", back_populates="approvals")


class DeadlineReminder(Base):
    __tablename__ = "deadline_reminders"

    id = Column(Integer, primary_key=True, index=True)
    laporan_id = Column(Integer, ForeignKey("laporans.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reminder_type = Column(String(20), nullable=False, index=True)  # "3_hari_lagi", "1_hari_lagi", "terlambat"
    is_sent = Column(Boolean, nullable=False, default=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Composite index untuk filter user + reminder status
    __table_args__ = (
        Index("ix_deadline_reminders_user_sent", "user_id", "is_sent"),
        Index("ix_deadline_reminders_laporan_type", "laporan_id", "reminder_type"),
    )

    laporan = relationship("Laporan")
    user = relationship("User")
