from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import Base, engine
from app.routers import auth, admin, lms, admin_lms, chatbot
from app.seed import seed_default_admin, seed_lms_dummy_data

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pramuka Jabar SuperApp - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(admin_lms.router, prefix="/api")
app.include_router(lms.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()
    seed_lms_dummy_data()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}
