from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_active_store, get_current_user
from app.services.common import unique_slug

router = APIRouter(tags=["stores"])


def _store_rating(db: Session, store: models.Store) -> Decimal | None:
    row = (
        db.query(func.avg(models.Review.rating))
        .join(models.Product, models.Review.product_id == models.Product.id)
        .filter(
            models.Product.store_id == store.id,
            models.Review.status == "visible",
        )
        .scalar()
    )
    return row.quantize(Decimal("0.1")) if row is not None else None


@router.get("/stores/{slug}", response_model=schemas.StorePublicOut)
def get_store_public(slug: str, db: Session = Depends(get_db)):
    store = db.query(models.Store).filter(models.Store.slug == slug).first()
    if not store or store.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Toko tidak ditemukan"
        )
    products = (
        db.query(models.Product)
        .filter(models.Product.store_id == store.id, models.Product.status == "active")
        .order_by(models.Product.sold.desc())
        .all()
    )
    return {
        "id": store.id,
        "name": store.name,
        "slug": store.slug,
        "description": store.description,
        "city": store.city,
        "province": store.province,
        "phone": store.phone,
        "rating": _store_rating(db, store),
        "products": products,
    }


@router.get("/seller/store", response_model=schemas.StoreOut)
def get_my_store(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    store = (
        db.query(models.Store)
        .filter(models.Store.owner_id == current_user.id)
        .order_by(models.Store.id.desc())
        .first()
    )
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Toko belum dibuat"
        )
    return store


@router.post("/seller/store", response_model=schemas.StoreOut, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: schemas.StoreCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active = (
        db.query(models.Store)
        .filter(models.Store.owner_id == current_user.id, models.Store.status == "active")
        .first()
    )
    if active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda sudah memiliki toko aktif",
        )
    store = models.Store(
        owner_id=current_user.id,
        name=payload.name,
        slug=unique_slug(db, models.Store, payload.name),
        description=payload.description,
        category_id=payload.category_id,
        city=payload.city,
        province=payload.province,
        phone=payload.phone,
        status="pending",
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.put("/seller/store", response_model=schemas.StoreOut)
def update_my_store(
    payload: schemas.StoreUpdate,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(store, field, value)
    db.commit()
    db.refresh(store)
    return store
