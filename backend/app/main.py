import time
from collections import defaultdict
from typing import Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import kegiatan as kegiatan_router
from app.routers import organisasi as organisasi_router
from app.routers import program as program_router
from app.routers import radit as radit_router
from app.seed import seed_default_admin, seed_realisasi_laporan_approval

Base.metadata.create_all(bind=engine)

# ─── Brute-force guard — in-memory rate limiter ────────────────────────────────
# Untuk production multi-instance, ganti dengan Redis-backed rate limiter.
_login_attempts: Dict[str, list] = defaultdict(list)
_LOGIN_WINDOW_SECONDS = 60
_LOGIN_MAX_ATTEMPTS = 10  # max 10 percobaan per IP per menit


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    attempts = _login_attempts[ip]
    # Buang attempt yang sudah di luar window
    _login_attempts[ip] = [t for t in attempts if now - t < _LOGIN_WINDOW_SECONDS]
    if len(_login_attempts[ip]) >= _LOGIN_MAX_ATTEMPTS:
        return True
    _login_attempts[ip].append(now)
    return False


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

# ─── Security headers middleware ───────────────────────────────────────────────

@app.middleware("http")
async def security_headers(request: Request, call_next):
    # Rate limit endpoint login
    if request.url.path in ("/api/auth/login", "/api/auth/register"):
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        if _is_rate_limited(client_ip):
            return Response(
                content='{"detail":"Terlalu banyak percobaan. Coba lagi dalam 1 menit."}',
                status_code=429,
                media_type="application/json",
            )

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
