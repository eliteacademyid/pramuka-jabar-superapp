import importlib.util
from pathlib import Path

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserDetailResponse,
    TokenResponse,
    TokenRefreshRequest,
)
from app.schemas.role import RoleBase, RoleCreate, RoleUpdate, RoleResponse
from app.schemas.organisasi import OrganisasiBase, OrganisasiCreate, OrganisasiUpdate, OrganisasiResponse
from app.schemas.program import ProgramBase, ProgramCreate, ProgramUpdate, ProgramResponse, ProgramDetailResponse
from app.schemas.kegiatan import KegiatanBase, KegiatanCreate, KegiatanUpdate, KegiatanResponse, KegiatanDetailResponse


def _load_legacy_schemas_module():
    module_path = Path(__file__).resolve().parent.parent / "schemas.py"
    spec = importlib.util.spec_from_file_location("app._legacy_schemas", module_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_legacy_schemas = _load_legacy_schemas_module()

if _legacy_schemas is not None:
    for _name in [
        "LoginRequest",
        "UserCreate",
        "UserUpdate",
        "UserOut",
        "Token",
        "TokenRefreshRequest",
        "RealisasiBase",
        "RealisasiCreate",
        "RealisasiUpdate",
        "DokumenResponse",
        "RealisasiResponse",
        "LaporanBase",
        "LaporanCreate",
        "LaporanResponse",
        "ApprovalCreate",
        "ApprovalResponse",
        "DashboardStatsResponse",
        "DashboardChartPoint",
        "DashboardComparisonResponse",
        "DashboardAnalyticsResponse",
    ]:
        globals()[_name] = getattr(_legacy_schemas, _name)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserDetailResponse",
    "TokenResponse",
    "TokenRefreshRequest",
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "OrganisasiBase",
    "OrganisasiCreate",
    "OrganisasiUpdate",
    "OrganisasiResponse",
    "ProgramBase",
    "ProgramCreate",
    "ProgramUpdate",
    "ProgramResponse",
    "ProgramDetailResponse",
    "KegiatanBase",
    "KegiatanCreate",
    "KegiatanUpdate",
    "KegiatanResponse",
    "KegiatanDetailResponse",
]

