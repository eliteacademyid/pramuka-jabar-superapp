from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

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


class Token(BaseModel):
    access_token: str
    token_type: str


class KegiatanCreate(BaseModel):
    nama_kegiatan: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    penanggung_jawab_id: int


class KegiatanUpdate(BaseModel):
    nama_kegiatan: Optional[str] = None
    deskripsi: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    penanggung_jawab_id: Optional[int] = None


class PJInfo(BaseModel):
    id: int
    nama_lengkap: str

    model_config = {"from_attributes": True}


class KegiatanOut(BaseModel):
    id: int
    nama_kegiatan: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    penanggung_jawab_id: int
    penanggung_jawab: Optional[PJInfo] = None
    dokumentasi: Optional["DokumentasiOut"] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusUpdate(BaseModel):
    status: str


class DokumentasiUpdate(BaseModel):
    catatan: Optional[str] = None


class FileDokumentasiOut(BaseModel):
    id: int
    nama_file: str
    ukuran: int
    tipe_file: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DokumentasiOut(BaseModel):
    id: int
    kegiatan_id: int
    catatan: Optional[str] = None
    files: list[FileDokumentasiOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KegiatanStats(BaseModel):
    total_kegiatan: int
    kegiatan_berlangsung: int
    kegiatan_selesai: int
