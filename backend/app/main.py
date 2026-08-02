from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import anggota as anggota_router
from app.routers import riwayat_jenjang as riwayat_router
from app.routers import kompetensi_master as kompetensi_router
from app.routers import capaian_kompetensi as capaian_router
from app.routers import referensi as referensi_router
from app.routers import rekap as rekap_router
from app.seed import seed_default_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Super Apps Pramuka Jawa Barat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(anggota_router.router, prefix="/api")
app.include_router(riwayat_router.router, prefix="/api")
app.include_router(kompetensi_router.router, prefix="/api")
app.include_router(capaian_router.router, prefix="/api")
app.include_router(referensi_router.router, prefix="/api")
app.include_router(rekap_router.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "modules": ["auth", "admin", "anggota", "riwayat_jenjang", "kompetensi_master", "capaian_kompetensi"]}


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error": type(exc).__name__}
    )
