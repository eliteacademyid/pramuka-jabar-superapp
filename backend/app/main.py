from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import admin as admin_router
from app.routers import auth as auth_router
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


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}
