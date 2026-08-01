from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text

from app.database import Base

ROLES = ("admin", "staff")

JENIS_SURAT = ("masuk", "keluar")

STATUS_SURAT = ("Draft", "Diverifikasi", "Didisposisi", "Diproses", "Selesai", "Diarsipkan")

STATUS_DISPOSISI = ("Belum Dibaca", "Dibaca", "Diproses", "Selesai")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Surat(Base):
    __tablename__ = "surat"

    id = Column(Integer, primary_key=True, index=True)
    nomor_surat = Column(String, nullable=True, index=True)
    jenis = Column(String, nullable=False)          # masuk / keluar
    pengirim = Column(String, nullable=True)
    tujuan = Column(String, nullable=True)
    tanggal_surat = Column(Date, nullable=True)
    tanggal_diterima = Column(Date, nullable=True)
    perihal = Column(String, nullable=False)
    isi = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Draft")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lampiran(Base):
    __tablename__ = "lampiran"

    id = Column(Integer, primary_key=True, index=True)
    surat_id = Column(Integer, ForeignKey("surat.id", ondelete="CASCADE"), nullable=False)
    nama_file = Column(String, nullable=False)
    lokasi_file = Column(Text, nullable=False)
    ukuran_file = Column(Integer, nullable=True)    # bytes
    tipe_file = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Disposisi(Base):
    __tablename__ = "disposisi"

    id = Column(Integer, primary_key=True, index=True)
    surat_id = Column(Integer, ForeignKey("surat.id", ondelete="CASCADE"), nullable=False)
    dari_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    kepada_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    catatan = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="Belum Dibaca")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    surat_id = Column(Integer, ForeignKey("surat.id", ondelete="CASCADE"), nullable=False)
    aktivitas = Column(String, nullable=False)
    keterangan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
