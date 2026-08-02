from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models import ROLES


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    role: str = "staff"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    nama_lengkap: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    nama_lengkap: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgramKerjaCreate(BaseModel):
    nama_program: str
    tahun_pelaksanaan: int
    penanggung_jawab: str
    status: str = "draft"


class ProgramKerjaUpdate(BaseModel):
    nama_program: Optional[str] = None
    tahun_pelaksanaan: Optional[int] = None
    penanggung_jawab: Optional[str] = None
    status: Optional[str] = None


class ProgramKerjaOut(BaseModel):
    id: int
    nama_program: str
    tahun_pelaksanaan: int
    penanggung_jawab: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AnggaranCreate(BaseModel):
    program_id: int
    kode_anggaran: str
    nama_anggaran: str
    pagu_anggaran: float = Field(gt=0)
    status: str = "draft"


class AnggaranUpdate(BaseModel):
    program_id: Optional[int] = None
    kode_anggaran: Optional[str] = None
    nama_anggaran: Optional[str] = None
    pagu_anggaran: Optional[float] = None
    status: Optional[str] = None


class AnggaranOut(BaseModel):
    id: int
    program_id: int
    kode_anggaran: str
    nama_anggaran: str
    pagu_anggaran: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RencanaBiayaCreate(BaseModel):
    anggaran_id: int
    nama_item: str
    volume: float = Field(gt=0)
    satuan: str
    harga_satuan: float = Field(gt=0)


class RencanaBiayaUpdate(BaseModel):
    anggaran_id: Optional[int] = None
    nama_item: Optional[str] = None
    volume: Optional[float] = None
    satuan: Optional[str] = None
    harga_satuan: Optional[float] = None


class RencanaBiayaOut(BaseModel):
    id: int
    anggaran_id: int
    nama_item: str
    volume: float
    satuan: str
    harga_satuan: float
    subtotal: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RealisasiPengeluaranCreate(BaseModel):
    anggaran_id: int
    tanggal_transaksi: date
    uraian: str
    nominal: float = Field(gt=0)
    bukti_transaksi: str
    keterangan: Optional[str] = None


class RealisasiPengeluaranUpdate(BaseModel):
    anggaran_id: Optional[int] = None
    tanggal_transaksi: Optional[date] = None
    uraian: Optional[str] = None
    nominal: Optional[float] = None
    bukti_transaksi: Optional[str] = None
    keterangan: Optional[str] = None


class RealisasiPengeluaranOut(BaseModel):
    id: int
    anggaran_id: int
    tanggal_transaksi: date
    uraian: str
    nominal: float
    bukti_transaksi: str
    keterangan: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str
