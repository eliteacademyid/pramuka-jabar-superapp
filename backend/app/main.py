import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import disposisi as disposisi_router
from app.routers import lampiran as lampiran_router
from app.routers import surat_keluar as surat_keluar_router
from app.routers import surat_masuk as surat_masuk_router
from app.routers import tracking as tracking_router
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

# Static files untuk serving upload lampiran
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")
app.include_router(surat_masuk_router.router, prefix="/api")
app.include_router(surat_keluar_router.router, prefix="/api")
app.include_router(disposisi_router.router, prefix="/api")
app.include_router(lampiran_router.router, prefix="/api")
app.include_router(tracking_router.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}
