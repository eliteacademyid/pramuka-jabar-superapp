from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLAlchemyEnum, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Role(str, Enum):
    SUPERADMIN = "superadmin"
    ADMINKWARtIR = "admin_kwarcab"
    ADMINGUDEp = "admin_gudep"
    PEMBINA = "pembina"
    ANGGOTA = "anggota"


class Jenjang(str, Enum):
    SIOGA = "siaga"
    PENGGALANG = "penggalang"
    PENEGAK = "penegak"
    PANDAGA = "pandega"
    DEWASA = "dewasa"


class Wilayah(Base):
    __tablename__ = "wilayah"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    tingkat = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("wilayah.id"), nullable=True)
    
    # Relationship
    parent = relationship("Wilayah", remote_side=[id])
    anak = relationship("Wilayah", back_populates="parent")
    gudeps = relationship("Gudep", back_populates="wilayah")


class Gudep(Base):
    __tablename__ = "gudep"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    pangkalan = Column(String, nullable=True)
    wilayah_id = Column(Integer, ForeignKey("wilayah.id"), nullable=False)
    
    # Relationship
    wilayah = relationship("Wilayah", back_populates="gudeps")
    members = relationship("Anggota", back_populates="gudep")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False)
    wilayah_scope_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scope = relationship("User", remote_side=[id])
    anggota = relationship("Anggota", back_populates="user")
    log_entries = relationship("LogAudit", back_populates="user")


class Anggota(Base):
    __tablename__ = "anggota"

    id = Column(Integer, primary_key=True, index=True)
    nta = Column(String, unique=True, index=True, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    tanggal_lahir = Column(DateTime, nullable=False)
    jenis_kelamin = Column(String, nullable=False)
    jenjang = Column(String, nullable=False)
    alamat = Column(Text, nullable=True)
    status_aktif = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    gudep_id = Column(Integer, ForeignKey("gudep.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="anggota")
    gudep = relationship("Gudep", back_populates="members")
    riwayat_jenjang = relationship("RiwayatJenjang", back_populates="anggota")
    capaian_kompetensi = relationship("CapaianKompetensi", back_populates="anggota", foreign_keys="CapaianKompetensi.anggota_id")
    potensi_minat = relationship("PotensiMinat", back_populates="anggota")


class RiwayatJenjang(Base):
    __tablename__ = "riwayat_jenjang"

    id = Column(Integer, primary_key=True, index=True)
    anggota_id = Column(Integer, ForeignKey("anggota.id"), nullable=False)
    jenjang_lama = Column(String, nullable=False)
    jenjang_baru = Column(String, nullable=False)
    tanggal_mutasi = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    anggota = relationship("Anggota", back_populates="riwayat_jenjang")


class KompetensiMaster(Base):
    __tablename__ = "kompetensi_master"

    id = Column(Integer, primary_key=True, index=True)
    jenis = Column(String, nullable=False)
    jenjang = Column(String, nullable=False)
    nama_kompetensi = Column(String, nullable=False)
    tingkat = Column(String, nullable=False)
    tahun = Column(Integer, nullable=True)


class CapaianKompetensi(Base):
    __tablename__ = "capaian_kompetensi"

    id = Column(Integer, primary_key=True, index=True)
    anggota_id = Column(Integer, ForeignKey("anggota.id"), nullable=False)
    kompetensi_id = Column(Integer, ForeignKey("kompetensi_master.id"), nullable=False)
    tanggal_capai = Column(DateTime, default=datetime.utcnow)
    penguji_id = Column(Integer, ForeignKey("anggota.id"), nullable=False)
    
    # Relationships
    anggota = relationship("Anggota", back_populates="capaian_kompetensi", foreign_keys=[anggota_id])
    kompetensi = relationship("KompetensiMaster")
    penguji = relationship("Anggota", foreign_keys=[penguji_id])


class PotensiMinat(Base):
    __tablename__ = "potensi_minat"

    id = Column(Integer, primary_key=True, index=True)
    anggota_id = Column(Integer, ForeignKey("anggota.id"), nullable=False)
    kategori = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=True)
    
    # Relationship
    anggota = relationship("Anggota", back_populates="potensi_minat")


class LogAudit(Base):
    __tablename__ = "log_audit"

    id = Column(Integer, primary_key=True, index=True)
    pengguna_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    aksi = Column(String, nullable=False)
    entitas = Column(String, nullable=False)
    entitas_id = Column(Integer, nullable=False)
    detail = Column(Text, nullable=True)
    waktu = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="log_entries")
