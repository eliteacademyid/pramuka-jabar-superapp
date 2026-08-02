from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

ROLES = ("admin", "staff")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ProgramKerja(Base):
    __tablename__ = "program_kerja"

    id = Column(Integer, primary_key=True, index=True)
    nama_program = Column(String, nullable=False)
    tahun_pelaksanaan = Column(Integer, nullable=False)
    penanggung_jawab = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    anggaran = relationship("Anggaran", back_populates="program")


class Anggaran(Base):
    __tablename__ = "anggaran"

    id = Column(Integer, primary_key=True, index=True)
    kode_anggaran = Column(String, unique=True, index=True, nullable=False)
    nama_anggaran = Column(String, nullable=False)
    pagu_anggaran = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    program_id = Column(Integer, ForeignKey("program_kerja.id"), nullable=False)

    program = relationship("ProgramKerja", back_populates="anggaran")
    rencana_biaya = relationship("RencanaBiaya", back_populates="anggaran")
    realisasi_pengeluaran = relationship("RealisasiPengeluaran", back_populates="anggaran")


class RencanaBiaya(Base):
    __tablename__ = "rencana_biaya"

    id = Column(Integer, primary_key=True, index=True)
    nama_item = Column(String, nullable=False)
    volume = Column(Float, nullable=False)
    satuan = Column(String, nullable=False)
    harga_satuan = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    anggaran_id = Column(Integer, ForeignKey("anggaran.id"), nullable=False)

    anggaran = relationship("Anggaran", back_populates="rencana_biaya")


class RealisasiPengeluaran(Base):
    __tablename__ = "realisasi_pengeluaran"

    id = Column(Integer, primary_key=True, index=True)
    tanggal_transaksi = Column(Date, nullable=False)
    uraian = Column(String, nullable=False)
    nominal = Column(Float, nullable=False)
    bukti_transaksi = Column(String, nullable=False)
    keterangan = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    anggaran_id = Column(Integer, ForeignKey("anggaran.id"), nullable=False)

    anggaran = relationship("Anggaran", back_populates="realisasi_pengeluaran")
