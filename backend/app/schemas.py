from datetime import datetime
<<<<<<< HEAD
from typing import List, Optional

from pydantic import BaseModel, Field
=======
from typing import Optional

from pydantic import BaseModel
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)

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
<<<<<<< HEAD


class RealisasiBase(BaseModel):
    judul: str = Field(..., min_length=1)
    deskripsi: Optional[str] = None
    target: Optional[int] = None
    realisasi: Optional[int] = None
    periode: Optional[str] = None
    status: Optional[str] = "draft"
    program_id: Optional[int] = None
    kegiatan_id: Optional[int] = None


class RealisasiCreate(RealisasiBase):
    pass


class RealisasiUpdate(BaseModel):
    judul: Optional[str] = None
    deskripsi: Optional[str] = None
    target: Optional[int] = None
    realisasi: Optional[int] = None
    periode: Optional[str] = None
    status: Optional[str] = None
    program_id: Optional[int] = None
    kegiatan_id: Optional[int] = None


class DokumenResponse(BaseModel):
    id: int
    nama_file: str
    url: str
    tipe: Optional[str] = None
    ukuran: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RealisasiResponse(BaseModel):
    id: int
    judul: str
    deskripsi: Optional[str] = None
    target: Optional[int] = None
    realisasi: Optional[int] = None
    periode: Optional[str] = None
    status: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    program_id: Optional[int] = None
    kegiatan_id: Optional[int] = None
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    documents: List[DokumenResponse] = []

    model_config = {"from_attributes": True}


class LaporanBase(BaseModel):
    judul: str = Field(..., min_length=1)
    periode: Optional[str] = None
    deskripsi: Optional[str] = None
    status: Optional[str] = "draft"
    realisasi_id: Optional[int] = None


class LaporanCreate(LaporanBase):
    pass


class LaporanResponse(BaseModel):
    id: int
    judul: str
    periode: Optional[str] = None
    deskripsi: Optional[str] = None
    status: str
    realisasi_id: Optional[int] = None
    created_by_id: int
    approved_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ApprovalCreate(BaseModel):
    laporan_id: int
    status: str = Field(..., min_length=1)
    catatan: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: int
    laporan_id: int
    user_id: int
    status: str
    catatan: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStatsResponse(BaseModel):
    total_realisasi: int
    total_laporan: int
    total_disetujui: int
    total_pending: int


class DashboardChartPoint(BaseModel):
    bulan: str
    total_laporan: int
    total_realisasi: int


class DashboardComparisonResponse(BaseModel):
    target: int
    realisasi: int
    selisih: int
    persentase: float


class DashboardAnalyticsResponse(BaseModel):
    statistik: DashboardStatsResponse
    grafik: List[DashboardChartPoint]
    perbandingan: DashboardComparisonResponse
=======
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
