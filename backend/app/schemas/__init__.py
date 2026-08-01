# Satu sumber kebenaran untuk semua schema.
# Semua router import dari `app.schemas` — tidak ada dynamic import fragile.

# ── Sub-module schemas ────────────────────────────────────────────────────────
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

# ── Legacy/main schemas (auth, realisasi, laporan, approval, dashboard) ───────
from app.schemas.main import (
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
    # Auth / User
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
