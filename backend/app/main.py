import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
from app.routers import kegiatan as kegiatan_router
from app.seed import seed_default_admin

Base.metadata.create_all(bind=engine)

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)

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
app.include_router(kegiatan_router.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/health")
def health():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}


@app.get("/")
def root():
    if os.path.exists(FRONTEND_DIST):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    return {"message": "Super Apps Pramuka Jawa Barat API is running (no frontend build)"}


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="Not found")
    if not os.path.exists(FRONTEND_DIST):
        raise HTTPException(status_code=404, detail="Frontend not built")
    file_path = os.path.join(FRONTEND_DIST, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
