from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin, auth, badges, tkk, certificates, achievements, member_achievements
from app.seed import seed_default_data

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Super Apps Pramuka Jawa Barat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(badges.router, prefix="/api")
app.include_router(tkk.router, prefix="/api")
app.include_router(certificates.router, prefix="/api")
app.include_router(achievements.router, prefix="/api")
app.include_router(member_achievements.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_data()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "e-Prestasi module loaded"}
