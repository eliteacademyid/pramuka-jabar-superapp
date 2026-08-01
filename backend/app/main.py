from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import kegiatan as kegiatan_router
from app.routers import organisasi as organisasi_router
from app.routers import program as program_router
from app.routers import radit as radit_router
from app.seed import seed_default_admin, seed_realisasi_laporan_approval

Base.metadata.create_all(bind=engine)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Super Apps Pramuka Jawa Barat",
        version="1.0.0",
        description="API komprehensif untuk manajemen program, kegiatan, realisasi, laporan, dan approval Pramuka Jawa Barat",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://example.com/logo.png"}
    openapi_schema["info"]["contact"] = {
        "name": "Tim Backend Pramuka Jabar",
        "email": "backend@pramuka-jabar.id",
    }
    openapi_schema["info"]["version"] = "1.1.0"
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Local development"},
        {"url": "https://api.pramuka-jabar.id", "description": "Production"},
    ]
    openapi_schema["tags"] = tags_metadata
    app.openapi_schema = openapi_schema
    return app.openapi_schema


tags_metadata = [
    {"name": "Authentication", "description": "Autentikasi pengguna - Login, Register, Refresh Token, Logout"},
    {"name": "Organisasi", "description": "Manajemen Organisasi Pramuka"},
    {"name": "Programs", "description": "Manajemen Program Pramuka dengan CRUD, search, filter, dan pagination"},
    {"name": "Kegiatans", "description": "Manajemen Kegiatan Pramuka dengan CRUD, search, filter, dan pagination"},
    {"name": "Realisasi", "description": "Input realisasi, upload dokumen, dan dashboard analytics"},
    {"name": "Laporan", "description": "Pelaporan kegiatan dan workflow approval"},
]

app = FastAPI(
    title="Super Apps Pramuka Jawa Barat",
    description="API komprehensif untuk manajemen program dan kegiatan Pramuka Jawa Barat dengan sistem autentikasi JWT",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {
        "message": "Super Apps Pramuka Jawa Barat API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Check API health status."""
    return {"status": "ok"}
