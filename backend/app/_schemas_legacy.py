"""
Legacy/shared Pydantic schemas.

File ini adalah sumber tunggal untuk schema yang digunakan lintas router.
Jangan pernah import dari app.schemas.py langsung — selalu lewat app.schemas (package).
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enums ────────────────────────────────────────────────────────────────────

class RealisasiStatusEnum(str, Enum):
    draft     = "draft"
    submitted = "submitted"
    approved  = "approved"
    rejected  = "rejected"


class LaporanStatusEnum(str, Enum):
    draft     = "draft"
    submitted = "submitted"
    approved  = "approved"
    rejected  = "rejected"


class ApprovalStatusEnum(str, Enum):
    approved = "approved"
    rejected = "rejected"


class RoleEnum(str, Enum):
    admin = "admin"
    staff = "staff"


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, strip_whitespace=True)
    password: str = Field(..., min_length=1, max_length=128)


class UserCreate(BaseModel):
    """
    Digunakan di:
    - POST /api/auth/register  (role selalu 'staff', diabaikan)
    - POST /api/admin/users    (role dari payload dipakai)
    """
    username:     str      = Field(..., min_length=3, max_length=50, strip_whitespace=True)
    password:     str      = Field(..., min_length=6, max_length=128)
    nama_lengkap: str      = Field(..., min_length=1, max_length=100, strip_whitespace=True)
    role:         RoleEnum = RoleEnum.staff

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username hanya boleh berisi huruf, angka, _ dan -")
        return v.lower()


class UserUpdate(BaseModel):
    """
    Digunakan di PUT /api/admin/users/{id}.
    Semua field Optional — hanya field yang dikirim yang diupdate.
    """
    username:     Optional[str]      = Field(None, min_length=3, max_length=50, strip_whitespace=True)
    password:     Optional[str]      = Field(None, min_length=6, max_length=128)
    nama_lengkap: Optional[str]      = Field(None, min_length=1, max_length=100, strip_whitespace=True)
    role:         Optional[RoleEnum] = None
    is_active:    Optional[bool]     = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username hanya boleh berisi huruf, angka, _ dan -")
        return v.lower() if v else v


class UserOut(BaseModel):
    id:           int
    username:     str
    nama_lengkap: str
    role:         str
    is_active:    bool
    created_at:   datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type:   str


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


# ─── Realisasi ────────────────────────────────────────────────────────────────

class RealisasiBase(BaseModel):
    judul:       str                            = Field(..., min_length=1, max_length=200, strip_whitespace=True)
    deskripsi:   Optional[str]                  = Field(None, max_length=2000)
    target:      Optional[int]                  = Field(None, ge=0, le=10_000_000)
    realisasi:   Optional[int]                  = Field(None, ge=0, le=10_000_000)
    periode:     Optional[str]                  = Field(None, max_length=50, strip_whitespace=True)
    status:      Optional[RealisasiStatusEnum]  = RealisasiStatusEnum.draft
    program_id:  Optional[int]                  = Field(None, gt=0)
    kegiatan_id: Optional[int]                  = Field(None, gt=0)


class RealisasiCreate(RealisasiBase):
    pass


class RealisasiUpdate(BaseModel):
    judul:       Optional[str]                  = Field(None, min_length=1, max_length=200, strip_whitespace=True)
    deskripsi:   Optional[str]                  = Field(None, max_length=2000)
    target:      Optional[int]                  = Field(None, ge=0, le=10_000_000)
    realisasi:   Optional[int]                  = Field(None, ge=0, le=10_000_000)
    periode:     Optional[str]                  = Field(None, max_length=50)
    status:      Optional[RealisasiStatusEnum]  = None
    program_id:  Optional[int]                  = Field(None, gt=0)
    kegiatan_id: Optional[int]                  = Field(None, gt=0)


class DokumenResponse(BaseModel):
    id:         int
    nama_file:  str
    url:        str
    tipe:       Optional[str] = None
    ukuran:     Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RealisasiResponse(BaseModel):
    id:           int
    judul:        str
    deskripsi:    Optional[str]      = None
    target:       Optional[int]      = None
    realisasi:    Optional[int]      = None
    periode:      Optional[str]      = None
    status:       str
    file_url:     Optional[str]      = None
    file_name:    Optional[str]      = None
    program_id:   Optional[int]      = None
    kegiatan_id:  Optional[int]      = None
    created_by_id: int
    created_at:   datetime
    updated_at:   Optional[datetime] = None
    documents:    List[DokumenResponse] = []

    model_config = {"from_attributes": True}


# ─── Laporan ──────────────────────────────────────────────────────────────────

class LaporanBase(BaseModel):
    judul:        str                         = Field(..., min_length=1, max_length=200, strip_whitespace=True)
    periode:      Optional[str]               = Field(None, max_length=50, strip_whitespace=True)
    deskripsi:    Optional[str]               = Field(None, max_length=2000)
    status:       Optional[LaporanStatusEnum] = LaporanStatusEnum.draft
    realisasi_id: Optional[int]               = Field(None, gt=0)


class LaporanCreate(LaporanBase):
    pass


class LaporanResponse(BaseModel):
    id:             int
    judul:          str
    periode:        Optional[str]      = None
    deskripsi:      Optional[str]      = None
    status:         str
    realisasi_id:   Optional[int]      = None
    created_by_id:  int
    approved_by_id: Optional[int]      = None
    created_at:     datetime
    updated_at:     Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Approval ─────────────────────────────────────────────────────────────────

class ApprovalCreate(BaseModel):
    laporan_id: int                 = Field(..., gt=0)
    status:     ApprovalStatusEnum            # hanya 'approved' | 'rejected'
    catatan:    Optional[str]       = Field(None, max_length=1000, strip_whitespace=True)


class ApprovalResponse(BaseModel):
    id:         int
    laporan_id: int
    user_id:    int
    status:     str
    catatan:    Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Dashboard ────────────────────────────────────────────────────────────────

class DashboardStatsResponse(BaseModel):
    total_realisasi: int
    total_laporan:   int
    total_disetujui: int
    total_pending:   int


class DashboardChartPoint(BaseModel):
    bulan:           str
    total_laporan:   int
    total_realisasi: int


class DashboardComparisonResponse(BaseModel):
    target:     int
    realisasi:  int
    selisih:    int
    persentase: float


class DashboardAnalyticsResponse(BaseModel):
    statistik:    DashboardStatsResponse
    grafik:       List[DashboardChartPoint]
    perbandingan: DashboardComparisonResponse
