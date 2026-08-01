from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services.order_service import checkout as do_checkout

router = APIRouter(prefix="/cart", tags=["cart"])


def _cart_item_or_404(db: Session, user: models.User, item_id: int) -> models.CartItem:
    item = (
        db.query(models.CartItem)
        .filter(models.CartItem.id == item_id, models.CartItem.user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item keranjang tidak ditemukan"
        )
    return item


def _product_or_400(db: Session, product_id: int) -> models.Product:
    product = db.get(models.Product, product_id)
    if not product or product.status != "active" or product.store.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Produk tidak tersedia"
        )
    return product


def _cart_out(db: Session, user: models.User) -> schemas.CartOut:
    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == user.id)
        .join(models.Product, models.CartItem.product_id == models.Product.id)
        .all()
    )
    groups: dict[int, dict] = {}
    total = Decimal("0.00")
    for item in items:
        p = item.product
        g = groups.setdefault(
            p.store_id,
            {
                "store_id": p.store_id,
                "store_name": p.store.name,
                "store_slug": p.store.slug,
                "items": [],
                "subtotal": Decimal("0.00"),
            },
        )
        subtotal = Decimal(p.price) * item.qty
        g["subtotal"] += subtotal
        total += subtotal
        g["items"].append(
            schemas.CartItemOut(
                id=item.id,
                product_id=p.id,
                name=p.name,
                slug=p.slug,
                price=p.price,
                qty=item.qty,
                subtotal=subtotal,
                stock=p.stock,
                image=(p.images or [None])[0],
                out_of_stock=p.stock <= 0,
            )
        )
    return schemas.CartOut(
        groups=list(groups.values()),
        total=total.quantize(Decimal("0.01")),
    )


@router.get("", response_model=schemas.CartOut)
def get_cart(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _cart_out(db, current_user)


@router.post("/items", response_model=schemas.CartOut, status_code=status.HTTP_201_CREATED)
def add_item(
    payload: schemas.CartAdd,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = _product_or_400(db, payload.product_id)
    existing = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.user_id == current_user.id,
            models.CartItem.product_id == payload.product_id,
        )
        .first()
    )
    if existing:
        new_qty = existing.qty + payload.qty
        if new_qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Stok tidak mencukupi"
            )
        existing.qty = new_qty
    else:
        if payload.qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Stok tidak mencukupi"
            )
        db.add(
            models.CartItem(
                user_id=current_user.id, product_id=product.id, qty=payload.qty
            )
        )
    db.commit()
    return _cart_out(db, current_user)


@router.put("/items/{item_id}", response_model=schemas.CartOut)
def update_item(
    item_id: int,
    payload: schemas.CartUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = _cart_item_or_404(db, current_user, item_id)
    if payload.qty > item.product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Stok tidak mencukupi"
        )
    item.qty = payload.qty
    db.commit()
    return _cart_out(db, current_user)


@router.delete("/items/{item_id}", response_model=schemas.CartOut)
def delete_item(
    item_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = _cart_item_or_404(db, current_user, item_id)
    db.delete(item)
    db.commit()
    return _cart_out(db, current_user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()


@router.post("/checkout", response_model=schemas.CheckoutResult)
def checkout(
    payload: schemas.CheckoutRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    codes = do_checkout(db, current_user, payload.address_id)
    db.commit()
    return schemas.CheckoutResult(orders=codes)
