from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import organisasi as organisasi_router
from app.routers import program as program_router
from app.routers import kegiatan as kegiatan_router
from app.seed import seed_default_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Super Apps Pramuka Jawa Barat",
    description="API untuk manajemen program dan kegiatan Pramuka Jawa Barat",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(organisasi_router.router, prefix="/api")
app.include_router(program_router.router, prefix="/api")
app.include_router(kegiatan_router.router, prefix="/api")
app.include_router(admin_router.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/")
def root():
    return {
        "message": "Super Apps Pramuka Jawa Barat API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
