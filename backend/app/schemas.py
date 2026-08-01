from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models import GOLONGAN, JABATAN_DEWASA, ROLES


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


# ---------- Wilayah ----------


class KwarcabCreate(BaseModel):
    nama: str
    kode_wilayah: str
    alamat_sekretariat: Optional[str] = None
    ketua: Optional[str] = None


class KwarcabUpdate(BaseModel):
    nama: Optional[str] = None
    kode_wilayah: Optional[str] = None
    alamat_sekretariat: Optional[str] = None
    ketua: Optional[str] = None


class KwarcabOut(BaseModel):
    id: int
    nama: str
    kode_wilayah: str
    alamat_sekretariat: Optional[str]
    ketua: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class KwaranCreate(BaseModel):
    nama: str
    kwarcab_id: int
    ketua: Optional[str] = None


class KwaranUpdate(BaseModel):
    nama: Optional[str] = None
    kwarcab_id: Optional[int] = None
    ketua: Optional[str] = None


class KwaranOut(BaseModel):
    id: int
    nama: str
    kwarcab_id: int
    ketua: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class GudepCreate(BaseModel):
    nomor_gudep: str
    nama_pangkalan: str
    jenis_pangkalan: str = "sekolah"
    kwaran_id: int
    pembina_gudep: Optional[str] = None
    alamat: Optional[str] = None


class GudepUpdate(BaseModel):
    nomor_gudep: Optional[str] = None
    nama_pangkalan: Optional[str] = None
    jenis_pangkalan: Optional[str] = None
    kwaran_id: Optional[int] = None
    pembina_gudep: Optional[str] = None
    alamat: Optional[str] = None


class GudepOut(BaseModel):
    id: int
    nomor_gudep: str
    nama_pangkalan: str
    jenis_pangkalan: str
    kwaran_id: int
    pembina_gudep: Optional[str]
    alamat: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Anggota ----------


class AnggotaCreate(BaseModel):
    nis_anggota: str
    nama_lengkap: str
    jenis_kelamin: str = "L"
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    golongan: str
    jabatan_dewasa: Optional[str] = None
    gudep_id: int
    nomor_hp: Optional[str] = None
    status_aktif: bool = True
    tanggal_bergabung: Optional[date] = None
    foto_url: Optional[str] = None


class AnggotaUpdate(BaseModel):
    nis_anggota: Optional[str] = None
    nama_lengkap: Optional[str] = None
    jenis_kelamin: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    golongan: Optional[str] = None
    jabatan_dewasa: Optional[str] = None
    gudep_id: Optional[int] = None
    nomor_hp: Optional[str] = None
    status_aktif: Optional[bool] = None
    tanggal_bergabung: Optional[date] = None
    foto_url: Optional[str] = None


class AnggotaOut(BaseModel):
    id: int
    nis_anggota: str
    nama_lengkap: str
    jenis_kelamin: str
    tempat_lahir: Optional[str]
    tanggal_lahir: Optional[date]
    golongan: str
    jabatan_dewasa: Optional[str]
    gudep_id: int
    nomor_hp: Optional[str]
    status_aktif: bool
    tanggal_bergabung: Optional[date]
    foto_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
