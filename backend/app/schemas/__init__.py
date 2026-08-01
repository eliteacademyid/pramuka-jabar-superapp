"""
Package schemas — satu sumber kebenaran untuk semua Pydantic schema.

Semua schema didefinisikan di app/schemas.py (legacy) dan di-re-export dari sini.
Tidak ada dynamic import, tidak ada risk silent failure.
"""

# ── New modular schemas (dari sub-modul) ──────────────────────────────────────
from app.schemas.role import RoleBase, RoleCreate, RoleUpdate, RoleResponse
from app.schemas.organisasi import (
    OrganisasiBase,
    OrganisasiCreate,
    OrganisasiUpdate,
    OrganisasiResponse,
)
from app.schemas.program import (
    ProgramBase,
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
    ProgramDetailResponse,
)
from app.schemas.kegiatan import (
    KegiatanBase,
    KegiatanCreate,
    KegiatanUpdate,
    KegiatanResponse,
    KegiatanDetailResponse,
)

# ── Legacy / shared schemas (dari app/schemas.py) ─────────────────────────────
# Import eksplisit — tidak ada dynamic/importlib magic yang bisa gagal diam-diam.
from app.schemas.user import (
    UserBase,
    UserLogin,
    UserResponse,
    UserDetailResponse,
    TokenResponse,
)
from app._schemas_legacy import (
    # Auth
    LoginRequest,
    UserCreate,
    UserUpdate,
    UserOut,
    Token,
    TokenRefreshRequest,
    # Realisasi
    RealisasiBase,
    RealisasiCreate,
    RealisasiUpdate,
    DokumenResponse,
    RealisasiResponse,
    # Laporan
    LaporanBase,
    LaporanCreate,
    LaporanResponse,
    # Approval
    ApprovalCreate,
    ApprovalResponse,
    # Dashboard
    DashboardStatsResponse,
    DashboardChartPoint,
    DashboardComparisonResponse,
    DashboardAnalyticsResponse,
)

__all__ = [
    # Role
    "RoleBase", "RoleCreate", "RoleUpdate", "RoleResponse",
    # Organisasi
    "OrganisasiBase", "OrganisasiCreate", "OrganisasiUpdate", "OrganisasiResponse",
    # Program
    "ProgramBase", "ProgramCreate", "ProgramUpdate", "ProgramResponse", "ProgramDetailResponse",
    # Kegiatan
    "KegiatanBase", "KegiatanCreate", "KegiatanUpdate", "KegiatanResponse", "KegiatanDetailResponse",
    # User (new)
    "UserBase", "UserLogin", "UserResponse", "UserDetailResponse", "TokenResponse",
    # Auth (legacy)
    "LoginRequest", "UserCreate", "UserUpdate", "UserOut", "Token", "TokenRefreshRequest",
    # Realisasi
    "RealisasiBase", "RealisasiCreate", "RealisasiUpdate", "DokumenResponse", "RealisasiResponse",
    # Laporan
    "LaporanBase", "LaporanCreate", "LaporanResponse",
    # Approval
    "ApprovalCreate", "ApprovalResponse",
    # Dashboard
    "DashboardStatsResponse", "DashboardChartPoint", "DashboardComparisonResponse",
    "DashboardAnalyticsResponse",
]
