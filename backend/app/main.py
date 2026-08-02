from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import UPLOAD_DIR
from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import anggota as anggota_router
from app.routers import auth as auth_router
from app.routers import beranda as beranda_router
from app.routers import hub_admin as hub_admin_router
from app.routers import hub_kontributor as hub_kontributor_router
from app.routers import hub_publik as hub_publik_router
from app.routers import kegiatan_internal as kegiatan_router
from app.routers import marketplace
from app.routers import pelaporan as pelaporan_router
from app.routers import persuratan as persuratan_router
from app.routers import wilayah as wilayah_router
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

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth_router.router, prefix="/api")
app.include_router(beranda_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(wilayah_router.router, prefix="/api")
app.include_router(anggota_router.router, prefix="/api")
app.include_router(kegiatan_router.router, prefix="/api")
app.include_router(hub_kontributor_router.router, prefix="/api")
app.include_router(hub_admin_router.router, prefix="/api")
app.include_router(hub_publik_router.router, prefix="/api")
app.include_router(persuratan_router.router, prefix="/api")
app.include_router(pelaporan_router.router, prefix="/api")
app.include_router(marketplace.publik_router, prefix="/api")
app.include_router(marketplace.penjual_router, prefix="/api")
app.include_router(marketplace.admin_router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}
