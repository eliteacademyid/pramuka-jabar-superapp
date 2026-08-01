from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import (
    get_active_store,
    get_current_admin,
    get_current_user,
    require_staff_or_admin,
)

router = APIRouter(prefix="/admin", tags=["admin-shop"])


def _store_or_404(db: Session, store_id: int) -> models.Store:
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Toko tidak ditemukan"
        )
    return store


def _product_or_404(db: Session, product_id: int) -> models.Product:
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Produk tidak ditemukan"
        )
    return product


# ---------- Stores moderation ----------

@router.get("/stores", response_model=List[schemas.StoreOut])
def admin_list_stores(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    query = db.query(models.Store)
    if status_filter:
        query = query.filter(models.Store.status == status_filter)
    return query.order_by(models.Store.created_at.desc()).all()


@router.post("/stores/{store_id}/approve", response_model=schemas.StoreOut)
def admin_approve_store(
    store_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    store = _store_or_404(db, store_id)
    if store.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Toko tidak berstatus pending"
        )
    store.status = "active"
    store.reject_reason = None
    db.commit()
    db.refresh(store)
    return store


@router.post("/stores/{store_id}/reject", response_model=schemas.StoreOut)
def admin_reject_store(
    store_id: int,
    payload: schemas.StoreModerate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    store = _store_or_404(db, store_id)
    if not payload.reason or len(payload.reason.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Alasan penolakan wajib diisi (min 5 karakter)",
        )
    if store.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Toko tidak berstatus pending"
        )
    store.status = "rejected"
    store.reject_reason = payload.reason
    db.commit()
    db.refresh(store)
    return store


@router.post("/stores/{store_id}/suspend", response_model=schemas.StoreOut)
def admin_suspend_store(
    store_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    store = _store_or_404(db, store_id)
    store.status = "suspended"
    db.commit()
    db.refresh(store)
    return store


@router.post("/stores/{store_id}/activate", response_model=schemas.StoreOut)
def admin_activate_store(
    store_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    store = _store_or_404(db, store_id)
    store.status = "active"
    store.reject_reason = None
    db.commit()
    db.refresh(store)
    return store


# ---------- Products moderation ----------

@router.get("/products", response_model=List[schemas.ProductOut])
def admin_list_products(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    query = db.query(models.Product)
    if status_filter:
        query = query.filter(models.Product.status == status_filter)
    return query.order_by(models.Product.created_at.desc()).all()


@router.post("/products/{product_id}/deactivate", response_model=schemas.ProductOut)
def admin_deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    product = _product_or_404(db, product_id)
    product.status = "archived"
    db.commit()
    db.refresh(product)
    return product


# ---------- Orders & reports ----------

@router.get("/orders", response_model=List[schemas.OrderOut])
def admin_list_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    query = db.query(models.Order)
    if status_filter:
        query = query.filter(models.Order.status == status_filter)
    orders = query.order_by(models.Order.created_at.desc()).all()
    return [
        schemas.OrderOut(
            id=o.id,
            order_code=o.order_code,
            buyer_id=o.buyer_id,
            store_id=o.store_id,
            store_name=o.store.name if o.store else None,
            address_snapshot=o.address_snapshot,
            subtotal=o.subtotal,
            shipping_fee=o.shipping_fee,
            discount=o.discount,
            total=o.total,
            status=o.status,
            escrow_status=o.escrow_status,
            commission_rate=o.commission_rate,
            tracking_number=o.tracking_number,
            created_at=o.created_at,
            items=[
                schemas.OrderItemOut(
                    id=i.id,
                    product_id=i.product_id,
                    product_name=i.product_name,
                    unit_price=i.unit_price,
                    qty=i.qty,
                    total=i.total,
                )
                for i in o.items
            ],
            status_history=[
                schemas.OrderStatusHistoryOut(
                    id=h.id, status=h.status, note=h.note, created_at=h.created_at
                )
                for h in sorted(o.status_history, key=lambda h: h.created_at)
            ],
        )
        for o in orders
    ]


@router.get("/reports", response_model=schemas.AdminReport)
def admin_reports(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    since = datetime.utcnow() - timedelta(days=days)
    users = db.query(models.User).filter(models.User.created_at >= since).count()
    stores = db.query(models.Store).filter(models.Store.created_at >= since).count()
    products = db.query(models.Product).filter(models.Product.created_at >= since).count()

    status_rows = (
        db.query(models.Order.status, func.count(models.Order.id))
        .filter(models.Order.created_at >= since)
        .group_by(models.Order.status)
        .all()
    )
    orders_by_status = {s: c for s, c in status_rows}

    volume = (
        db.query(func.coalesce(func.sum(models.Order.total), 0))
        .filter(
            models.Order.created_at >= since,
            models.Order.status == "completed",
        )
        .scalar()
    )

    return schemas.AdminReport(
        users=users,
        stores=stores,
        products=products,
        orders_by_status=orders_by_status,
        transaction_volume=Decimal(str(volume)),
        period_days=days,
    )


@router.get("/carts", response_model=List[schemas.AdminCartEntryOut])
def admin_list_carts(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_staff_or_admin),
):
    users = db.query(models.User).order_by(models.User.id).all()
    items = (
        db.query(models.CartItem)
        .join(models.Product, models.CartItem.product_id == models.Product.id)
        .order_by(models.CartItem.user_id, models.CartItem.id)
        .all()
    )
    by_user: dict[int, List[models.CartItem]] = {}
    for it in items:
        by_user.setdefault(it.user_id, []).append(it)

    entries: List[schemas.AdminCartEntryOut] = []
    for u in users:
        u_items = by_user.get(u.id, [])
        item_rows: List[schemas.AdminCartItemOut] = []
        subtotal = Decimal("0.00")
        qty_total = 0
        updated_at: Optional[datetime] = None
        for it in u_items:
            price = Decimal(it.product.price)
            sub = price * it.qty
            subtotal += sub
            qty_total += it.qty
            if updated_at is None or it.created_at > updated_at:
                updated_at = it.created_at
            item_rows.append(
                schemas.AdminCartItemOut(
                    product_id=it.product_id,
                    name=it.product.name,
                    price=price,
                    qty=it.qty,
                    subtotal=sub.quantize(Decimal("0.01")),
                )
            )
        entries.append(
            schemas.AdminCartEntryOut(
                user_id=u.id,
                username=u.username,
                nama_lengkap=u.nama_lengkap,
                is_active=u.is_active,
                item_count=len(u_items),
                qty_total=qty_total,
                subtotal=subtotal.quantize(Decimal("0.01")),
                updated_at=updated_at,
                items=item_rows,
            )
        )
    return entries


# ---------- Seller dashboard ----------

seller_router = APIRouter(prefix="/seller", tags=["seller"])


@seller_router.get("/dashboard", response_model=schemas.SellerDashboardOut)
def seller_dashboard(
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    active_products = (
        db.query(models.Product)
        .filter(models.Product.store_id == store.id, models.Product.status == "active")
        .count()
    )
    status_rows = (
        db.query(models.Order.status, func.count(models.Order.id))
        .filter(models.Order.store_id == store.id)
        .group_by(models.Order.status)
        .all()
    )
    orders_by_status = {s: c for s, c in status_rows}
    total_sales = (
        db.query(func.coalesce(func.sum(models.Order.total), 0))
        .filter(models.Order.store_id == store.id, models.Order.status == "completed")
        .scalar()
    )
    wallet = (
        db.query(models.Wallet)
        .filter(models.Wallet.user_id == store.owner_id)
        .first()
    )
    return schemas.SellerDashboardOut(
        active_products=active_products,
        orders_by_status=orders_by_status,
        total_sales=Decimal(str(total_sales)),
        balance=wallet.balance if wallet else Decimal("0.00"),
        escrow_balance=wallet.escrow_balance if wallet else Decimal("0.00"),
    )
