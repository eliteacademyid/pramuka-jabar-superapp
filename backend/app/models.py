from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base

ROLES = ("admin", "staff")

GOLONGAN = ("siaga", "penggalang", "penegak", "pandega", "dewasa")
JABATAN_DEWASA = ("Pembina Pramuka", "Pelatih", "Andalan", "Lainnya")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Kwarcab(Base):
    __tablename__ = "kwarcab"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    kode_wilayah = Column(String, unique=True, nullable=False)
    alamat_sekretariat = Column(Text, nullable=True)
    ketua = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    kwaran = relationship("Kwaran", back_populates="kwarcab")


class Kwaran(Base):
    __tablename__ = "kwaran"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    kwarcab_id = Column(
        Integer, ForeignKey("kwarcab.id"), nullable=False, index=True
    )
    ketua = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    kwarcab = relationship("Kwarcab", back_populates="kwaran")
    gudep = relationship("Gudep", back_populates="kwaran")


class Gudep(Base):
    __tablename__ = "gudep"

    id = Column(Integer, primary_key=True, index=True)
    nomor_gudep = Column(String, nullable=False)
    nama_pangkalan = Column(String, nullable=False)
    jenis_pangkalan = Column(String, nullable=False, default="sekolah")
    kwaran_id = Column(
        Integer, ForeignKey("kwaran.id"), nullable=False, index=True
    )
    pembina_gudep = Column(String, nullable=True)
    alamat = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    kwaran = relationship("Kwaran", back_populates="gudep")
    anggota = relationship("Anggota", back_populates="gudep")


class Anggota(Base):
    __tablename__ = "anggota"

    id = Column(Integer, primary_key=True, index=True)
    nis_anggota = Column(String, unique=True, index=True, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    jenis_kelamin = Column(String, nullable=False, default="L")
    tempat_lahir = Column(String, nullable=True)
    tanggal_lahir = Column(Date, nullable=True)
    golongan = Column(String, nullable=False, default="siaga")
    jabatan_dewasa = Column(String, nullable=True)
    gudep_id = Column(
        Integer, ForeignKey("gudep.id"), nullable=False, index=True
    )
    nomor_hp = Column(String, nullable=True)
    status_aktif = Column(Boolean, nullable=False, default=True)
    tanggal_bergabung = Column(Date, nullable=True)
    foto_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    gudep = relationship("Gudep", back_populates="anggota")
