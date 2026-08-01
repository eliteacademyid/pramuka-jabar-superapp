from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models import ROLES


# ─── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ─── User ─────────────────────────────────────────────────────────────────────

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


class UserSimple(BaseModel):
    id: int
    username: str
    nama_lengkap: str
    role: str

    model_config = {"from_attributes": True}


# ─── Lampiran ────────────────────────────────────────────────────────────────

class LampiranOut(BaseModel):
    id: int
    surat_id: int
    nama_file: str
    lokasi_file: str
    ukuran_file: Optional[int] = None
    tipe_file: Optional[str] = None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


# ─── Disposisi ───────────────────────────────────────────────────────────────

class DisposisiCreate(BaseModel):
    surat_id: int
    kepada_user: int
    catatan: Optional[str] = None
    deadline: Optional[datetime] = None


class DisposisiUpdate(BaseModel):
    status: str
    catatan: Optional[str] = None


class DisposisiOut(BaseModel):
    id: int
    surat_id: int
    dari_user: int
    kepada_user: int
    catatan: Optional[str] = None
    deadline: Optional[datetime] = None
    status: str
    created_at: datetime
    updated_at: datetime
    dari_user_info: Optional[UserSimple] = None
    kepada_user_info: Optional[UserSimple] = None

    model_config = {"from_attributes": True}


# ─── Surat ───────────────────────────────────────────────────────────────────

class SuratCreate(BaseModel):
    jenis: str                              # masuk / keluar
    pengirim: Optional[str] = None
    tujuan: Optional[str] = None
    tanggal_surat: Optional[date] = None
    tanggal_diterima: Optional[date] = None
    perihal: str
    isi: Optional[str] = None
    status: Optional[str] = "Draft"


class SuratUpdate(BaseModel):
    nomor_surat: Optional[str] = None
    pengirim: Optional[str] = None
    tujuan: Optional[str] = None
    tanggal_surat: Optional[date] = None
    tanggal_diterima: Optional[date] = None
    perihal: Optional[str] = None
    isi: Optional[str] = None
    status: Optional[str] = None


class SuratOut(BaseModel):
    id: int
    nomor_surat: Optional[str] = None
    jenis: str
    pengirim: Optional[str] = None
    tujuan: Optional[str] = None
    tanggal_surat: Optional[date] = None
    tanggal_diterima: Optional[date] = None
    perihal: str
    isi: Optional[str] = None
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    lampiran: List[LampiranOut] = []
    disposisi: List[DisposisiOut] = []
    created_by_info: Optional[UserSimple] = None

    model_config = {"from_attributes": True}


class SuratListOut(BaseModel):
    id: int
    nomor_surat: Optional[str] = None
    jenis: str
    pengirim: Optional[str] = None
    tujuan: Optional[str] = None
    tanggal_surat: Optional[date] = None
    perihal: str
    status: str
    created_at: datetime
    created_by_info: Optional[UserSimple] = None

    model_config = {"from_attributes": True}


# ─── Audit Log ───────────────────────────────────────────────────────────────

class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    surat_id: int
    aktivitas: str
    keterangan: Optional[str] = None
    created_at: datetime
    user_info: Optional[UserSimple] = None

    model_config = {"from_attributes": True}
