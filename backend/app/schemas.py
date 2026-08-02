from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models import Role, Jenjang


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    role: Role = Role.ANGGOTA
    wilayah_scope_id: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    nama_lengkap: Optional[str] = None
    role: Optional[Role] = None
    wilayah_scope_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    nama_lengkap: str
    role: Role
    wilayah_scope_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


# SDD Models
class WilayahCreate(BaseModel):
    nama: str
    tingkat: str
    parent_id: Optional[int] = None


class WilayahOut(BaseModel):
    id: int
    nama: str
    tingkat: str
    parent_id: Optional[int] = None

    model_config = {"from_attributes": True}


class GudepCreate(BaseModel):
    nama: str
    pangkalan: Optional[str] = None
    wilayah_id: Optional[int] = None


class GudepOut(BaseModel):
    id: int
    nama: str
    pangkalan: Optional[str] = None
    wilayah_id: int

    model_config = {"from_attributes": True}


class AnggotaCreate(BaseModel):
    nta: str
    nama_lengkap: str
    tanggal_lahir: datetime
    jenis_kelamin: str
    jenjang: Jenjang
    status_aktif: bool = True
    gudep_id: int


class AnggotaOut(BaseModel):
    id: int
    nta: str
    nama_lengkap: str
    tanggal_lahir: datetime
    jenis_kelamin: str
    jenjang: Jenjang
    status_aktif: bool
    gudep_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RiwayatJenjangCreate(BaseModel):
    anggota_id: int
    jenjang_lama: Jenjang
    jenjang_baru: Jenjang
    tanggal_mutasi: Optional[datetime] = None


class RiwayatJenjangOut(BaseModel):
    id: int
    anggota_id: int
    jenjang_lama: Jenjang
    jenjang_baru: Jenjang
    tanggal_mutasi: datetime

    model_config = {"from_attributes": True}


class KompetensiMasterOut(BaseModel):
    id: int
    jenis: str
    jenjang: Jenjang
    nama_kompetensi: str
    tingkat: str

    model_config = {"from_attributes": True}


class CapaianKompetensiCreate(BaseModel):
    anggota_id: int
    kompetensi_id: int
    tanggal_capai: Optional[datetime] = None
    penguji_id: int


class CapaianKompetensiOut(BaseModel):
    id: int
    anggota_id: int
    kompetensi_id: int
    tanggal_capai: datetime
    penguji_id: int

    model_config = {"from_attributes": True}


class PotensiMinatCreate(BaseModel):
    anggota_id: int
    kategori: str
    deskripsi: Optional[str] = None


class PotensiMinatOut(BaseModel):
    id: int
    anggota_id: int
    kategori: str
    deskripsi: Optional[str] = None

    model_config = {"from_attributes": True}


class LogAuditOut(BaseModel):
    id: int
    pengguna_id: int
    aksi: str
    entitas: str
    entitas_id: int
    detail: Optional[str] = None
    waktu: datetime

    model_config = {"from_attributes": True}


# Filter & Search Models
class AnggotaFilter(BaseModel):
    nama: Optional[str] = None
    nta: Optional[str] = None
    jenjang: Optional[Jenjang] = None
    wilayah_id: Optional[int] = None
    status_aktif: Optional[bool] = None


class WilayahFilter(BaseModel):
    nama: Optional[str] = None
    tingkat: Optional[str] = None


class CapaianKompetensiFilter(BaseModel):
    anggota_id: Optional[int] = None
    kompetensi_id: Optional[int] = None
    jenjang: Optional[Jenjang] = None
