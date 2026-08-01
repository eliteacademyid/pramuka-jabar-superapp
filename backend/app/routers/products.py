from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_active_store
from app.services.common import unique_slug

router = APIRouter(tags=["products"])


def _ratings_map(db: Session, product_ids: list[int]) -> dict[int, Decimal]:
    if not product_ids:
        return {}
    rows = (
        db.query(models.Review.product_id, func.avg(models.Review.rating))
        .filter(
            models.Review.product_id.in_(product_ids),
            models.Review.status == "visible",
        )
        .group_by(models.Review.product_id)
        .all()
    )
    return {
        pid: Decimal(str(avg)).quantize(Decimal("0.1"))
        for pid, avg in rows
        if avg is not None
    }


def _to_public(product: models.Product, rating: Optional[Decimal]) -> dict:
    data = {
        "id": product.id,
        "store_id": product.store_id,
        "category_id": product.category_id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "unit": product.unit,
        "images": product.images or [],
        "status": product.status,
        "sold": product.sold,
        "rating": rating,
        "created_at": product.created_at,
        "out_of_stock": product.stock <= 0,
        "store": {
            "id": product.store.id,
            "name": product.store.name,
            "slug": product.store.slug,
            "status": product.store.status,
            "city": product.store.city,
        },
    }
    return data


@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.name).all()


@router.get("/cities", response_model=List[str])
def list_cities(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Store.city)
        .filter(models.Store.status == "active")
        .filter(func.coalesce(models.Store.city, "") != "")
        .distinct()
        .order_by(models.Store.city)
        .all()
    )
    return [city for (city,) in rows]


@router.get("/products/suggest", response_model=List[schemas.ProductSuggestionOut])
def suggest_products(
    q: str = Query(min_length=1, max_length=80),
    limit: int = Query(default=6, ge=1, le=10),
    db: Session = Depends(get_db),
):
    like = f"%{q.lower()}%"
    rows = (
        db.query(models.Product)
        .join(models.Store, models.Product.store_id == models.Store.id)
        .join(models.Category, models.Product.category_id == models.Category.id)
        .filter(
            models.Product.status == "active",
            models.Store.status == "active",
            func.lower(models.Product.name).like(like),
        )
        .order_by(models.Product.sold.desc(), models.Product.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        schemas.ProductSuggestionOut(
            id=p.id,
            name=p.name,
            slug=p.slug,
            price=p.price,
            image=(p.images or [None])[0],
            category_slug=p.category.slug,
            store_name=p.store.name,
            sold=p.sold,
        )
        for p in rows
    ]


@router.get("/products", response_model=schemas.ProductPage)
def list_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    sort: str = Query(default="newest", pattern="^(newest|cheapest|expensive|bestseller|rating|reviewed)$"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Product)
        .join(models.Store, models.Product.store_id == models.Store.id)
        .filter(models.Product.status == "active", models.Store.status == "active")
    )
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            func.lower(models.Product.name).like(like)
            | func.lower(func.coalesce(models.Product.description, "")).like(like)
        )
    if category:
        query = query.join(models.Category, models.Product.category_id == models.Category.id).filter(
            models.Category.slug == category
        )
    if city:
        query = query.filter(
            func.lower(models.Store.city).like(f"%{city.lower()}%")
        )
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    total = query.count()
    if sort == "cheapest":
        query = query.order_by(models.Product.price.asc())
    elif sort == "expensive":
        query = query.order_by(models.Product.price.desc())
    elif sort == "bestseller":
        query = query.order_by(models.Product.sold.desc())
    elif sort == "rating":
        query = (
            query.outerjoin(
                models.Review,
                (models.Review.product_id == models.Product.id)
                & (models.Review.status == "visible"),
            )
            .group_by(models.Product.id)
            .order_by(
                func.avg(models.Review.rating).desc().nulls_last(),
                models.Product.sold.desc(),
            )
        )
    elif sort == "reviewed":
        query = (
            query.outerjoin(
                models.Review,
                (models.Review.product_id == models.Product.id)
                & (models.Review.status == "visible"),
            )
            .group_by(models.Product.id)
            .order_by(
                func.count(models.Review.id).desc().nulls_last(),
                models.Product.sold.desc(),
            )
        )
    else:
        query = query.order_by(models.Product.created_at.desc())

    products = query.offset((page - 1) * size).limit(size).all()
    ratings = _ratings_map(db, [p.id for p in products])
    return schemas.ProductPage(
        items=[schemas.ProductPublicOut(**(_to_public(p, ratings.get(p.id)))) for p in products],
        total=total,
        page=page,
        size=size,
    )


@router.get("/products/{slug}", response_model=schemas.ProductPublicOut)
def get_product(slug: str, db: Session = Depends(get_db)):
    product = (
        db.query(models.Product)
        .filter(models.Product.slug == slug, models.Product.status == "active")
        .first()
    )
    if not product or product.store.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan"
        )
    reviews = (
        db.query(models.Review)
        .filter(models.Review.product_id == product.id, models.Review.status == "visible")
        .order_by(models.Review.created_at.desc())
        .all()
    )
    data = _to_public(product, _ratings_map(db, [product.id]).get(product.id))
    data["reviews"] = [
        {
            "id": r.id,
            "order_item_id": r.order_item_id,
            "user_id": r.user_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "comment": r.comment,
            "status": r.status,
            "created_at": r.created_at,
            "username": r.user.username if r.user else None,
        }
        for r in reviews
    ]
    return data


# ---------- Seller ----------

@router.get("/seller/products", response_model=List[schemas.ProductOut])
def list_my_products(
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    products = (
        db.query(models.Product)
        .filter(models.Product.store_id == store.id)
        .order_by(models.Product.created_at.desc())
        .all()
    )
    ratings = _ratings_map(db, [p.id for p in products])
    return [
        schemas.ProductOut(
            id=p.id,
            store_id=p.store_id,
            category_id=p.category_id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            price=p.price,
            stock=p.stock,
            unit=p.unit,
            images=p.images or [],
            status=p.status,
            sold=p.sold,
            rating=ratings.get(p.id),
            created_at=p.created_at,
        )
        for p in products
    ]


@router.post("/seller/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: schemas.ProductCreate,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    if payload.status not in ("draft", "active", "archived"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Status produk tidak valid"
        )
    product = models.Product(
        store_id=store.id,
        category_id=payload.category_id,
        name=payload.name,
        slug=unique_slug(db, models.Product, payload.name),
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        unit=payload.unit,
        images=payload.images or [],
        status=payload.status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def _get_my_product_or_404(db: Session, store: models.Store, product_id: int) -> models.Product:
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id, models.Product.store_id == store.id)
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan"
        )
    return product


@router.get("/seller/products/{product_id}", response_model=schemas.ProductOut)
def get_my_product(
    product_id: int,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    product = _get_my_product_or_404(db, store, product_id)
    rating = _ratings_map(db, [product.id]).get(product.id)
    return schemas.ProductOut(
        id=product.id,
        store_id=product.store_id,
        category_id=product.category_id,
        name=product.name,
        slug=product.slug,
        description=product.description,
        price=product.price,
        stock=product.stock,
        unit=product.unit,
        images=product.images or [],
        status=product.status,
        sold=product.sold,
        rating=rating,
        created_at=product.created_at,
    )


@router.put("/seller/products/{product_id}", response_model=schemas.ProductOut)
def update_my_product(
    product_id: int,
    payload: schemas.ProductUpdate,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    product = _get_my_product_or_404(db, store, product_id)
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] not in ("draft", "active", "archived"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Status produk tidak valid"
        )
    for field, value in data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/seller/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_product(
    product_id: int,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    product = _get_my_product_or_404(db, store, product_id)
    db.delete(product)
    db.commit()
