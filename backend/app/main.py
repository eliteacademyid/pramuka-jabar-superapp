from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.database import Base, engine
from app.limiter import limiter
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import kegiatan as kegiatan_router
from app.routers import organisasi as organisasi_router
from app.routers import program as program_router
from app.routers import radit as radit_router
from app.routers import reminder as reminder_router
from app.routers import kpi as kpi_router
from app.seed import seed_default_admin, seed_realisasi_laporan_approval

Base.metadata.create_all(bind=engine)


# ─── App setup ─────────────────────────────────────────────────────────────────

# Sembunyikan docs di production — tidak perlu publik melihat schema API
_docs_url = None if settings.is_production else "/docs"
_redoc_url = None if settings.is_production else "/redoc"
_openapi_url = None if settings.is_production else "/openapi.json"


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Super Apps Pramuka Jawa Barat",
        version="1.0.0",
        description="API Pramuka Jawa Barat",
        routes=app.routes,
    )
    openapi_schema["info"]["contact"] = {"name": "Tim Backend", "email": "backend@pramuka-jabar.id"}
    openapi_schema["info"]["version"] = "1.1.0"
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Local"},
        {"url": "https://api.pramuka-jabar.id", "description": "Production"},
    ]
    openapi_schema["tags"] = tags_metadata
    app.openapi_schema = openapi_schema
    return app.openapi_schema


tags_metadata = [
    {"name": "Authentication", "description": "Login, Register, Refresh, Logout"},
    {"name": "Organisasi", "description": "Manajemen Organisasi"},
    {"name": "Programs", "description": "Manajemen Program"},
    {"name": "Kegiatans", "description": "Manajemen Kegiatan"},
    {"name": "Realisasi", "description": "Realisasi, Laporan, Approval, Dashboard"},
    {"name": "Deadline Reminders", "description": "Notifikasi dan monitoring deadline laporan"},
    {"name": "Dashboard KPI", "description": "KPI organisasi - Program selesai, terlambat, gagal, aktif"},
    {"name": "Admin", "description": "Manajemen User (Admin only)"},
]

app = FastAPI(
    title="Super Apps Pramuka Jawa Barat",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)
app.openapi = custom_openapi

# ─── SlowAPI rate limiter ──────────────────────────────────────────────────────
# Daftarkan state limiter dan exception handler agar @limiter.limit bekerja.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ─── Security headers middleware ───────────────────────────────────────────────

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    # Tambah security headers di setiap response
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ─── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=600,
)

# ─── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router.router, prefix="/api")
app.include_router(organisasi_router.router, prefix="/api")
app.include_router(program_router.router, prefix="/api")
app.include_router(kegiatan_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(radit_router.radit_router, prefix="/api")
app.include_router(reminder_router.router, prefix="/api")
app.include_router(kpi_router.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    try:
        seed_default_admin()
        seed_realisasi_laporan_approval()
    except Exception as exc:
        print(f"Startup seed warning: {exc}")


@app.get("/", tags=["Root"])
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
