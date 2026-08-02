from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    admin as admin_router,
    admin_shop,
    auth as auth_router,
    cart,
    chat,
    me as me_router,
    notifications,
    orders,
    products,
    reviews,
    stores,
    tickets,
    wallet,
)
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
app.include_router(me_router.router, prefix="/api")
app.include_router(stores.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(wallet.router, prefix="/api")
app.include_router(wallet.admin_router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(tickets.router, prefix="/api")
app.include_router(tickets.admin_router, prefix="/api")
app.include_router(admin_shop.router, prefix="/api")
app.include_router(admin_shop.seller_router, prefix="/api")


@app.on_event("startup")
def startup_seed():
    seed_default_admin()


@app.get("/")
def root():
    return {"message": "Super Apps Pramuka Jawa Barat API is running"}
