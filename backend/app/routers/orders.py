from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_active_store, get_current_user
from app.services.order_service import cancel_order, confirm_receipt
from app.services.wallet_service import pay_order

router = APIRouter(tags=["orders"])


def _order_or_404(db: Session, code: str) -> models.Order:
    order = db.query(models.Order).filter(models.Order.order_code == code).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order tidak ditemukan"
        )
    return order


def _order_out(order: models.Order) -> schemas.OrderOut:
    return schemas.OrderOut(
        id=order.id,
        order_code=order.order_code,
        buyer_id=order.buyer_id,
        store_id=order.store_id,
        store_name=order.store.name if order.store else None,
        address_snapshot=order.address_snapshot,
        subtotal=order.subtotal,
        shipping_fee=order.shipping_fee,
        discount=order.discount,
        total=order.total,
        status=order.status,
        escrow_status=order.escrow_status,
        commission_rate=order.commission_rate,
        tracking_number=order.tracking_number,
        created_at=order.created_at,
        items=[
            schemas.OrderItemOut(
                id=i.id,
                product_id=i.product_id,
                product_name=i.product_name,
                unit_price=i.unit_price,
                qty=i.qty,
                total=i.total,
            )
            for i in order.items
        ],
        status_history=[
            schemas.OrderStatusHistoryOut(
                id=h.id,
                status=h.status,
                note=h.note,
                created_at=h.created_at,
            )
            for h in sorted(order.status_history, key=lambda h: h.created_at)
        ],
    )


def _can_access(order: models.Order, user: models.User) -> bool:
    if user.role == "admin":
        return True
    if order.buyer_id == user.id:
        return True
    if order.store_id and order.store.owner_id == user.id:
        return True
    return False


@router.get("/orders", response_model=List[schemas.OrderOut])
def list_my_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Order).filter(models.Order.buyer_id == current_user.id)
    if status_filter:
        query = query.filter(models.Order.status == status_filter)
    orders = query.order_by(models.Order.created_at.desc()).all()
    return [_order_out(o) for o in orders]


@router.get("/orders/{code}", response_model=schemas.OrderOut)
def get_order(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = _order_or_404(db, code)
    if not _can_access(order, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    return _order_out(order)


@router.post("/orders/{code}/pay", response_model=schemas.OrderOut)
def pay_my_order(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = _order_or_404(db, code)
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    pay_order(db, order)
    db.commit()
    db.refresh(order)
    return _order_out(order)


@router.post("/orders/{code}/cancel", response_model=schemas.OrderOut)
def cancel_my_order(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = _order_or_404(db, code)
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    cancel_order(db, order)
    db.commit()
    db.refresh(order)
    return _order_out(order)


@router.post("/orders/{code}/confirm-receipt", response_model=schemas.OrderOut)
def confirm_receipt_endpoint(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = _order_or_404(db, code)
    if order.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses"
        )
    confirm_receipt(db, order)
    db.commit()
    db.refresh(order)
    return _order_out(order)


# ---------- Seller ----------

@router.get("/seller/orders", response_model=List[schemas.OrderOut])
def list_seller_orders(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    query = db.query(models.Order).filter(models.Order.store_id == store.id)
    if status_filter:
        query = query.filter(models.Order.status == status_filter)
    orders = query.order_by(models.Order.created_at.desc()).all()
    return [_order_out(o) for o in orders]


@router.get("/seller/orders/{order_id}", response_model=schemas.OrderOut)
def get_seller_order(
    order_id: int,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    return _order_out(_seller_order_or_404(db, store, order_id))


def _seller_order_or_404(db: Session, store: models.Store, order_id: int) -> models.Order:
    order = (
        db.query(models.Order)
        .filter(models.Order.id == order_id, models.Order.store_id == store.id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order tidak ditemukan"
        )
    return order


@router.post("/seller/orders/{order_id}/confirm", response_model=schemas.OrderOut)
def seller_confirm_order(
    order_id: int,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    order = _seller_order_or_404(db, store, order_id)
    if order.status != "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order belum dibayar, tidak dapat dikonfirmasi",
        )
    order.status = "processed"
    db.add(models.OrderStatusHistory(order_id=order.id, status="processed"))
    db.commit()
    db.refresh(order)
    return _order_out(order)


class ShipRequest(BaseModel):
    tracking_number: str = ""


@router.post("/seller/orders/{order_id}/ship", response_model=schemas.OrderOut)
def seller_ship_order(
    order_id: int,
    payload: ShipRequest,
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    order = _seller_order_or_404(db, store, order_id)
    if order.status not in ("paid", "processed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order tidak dapat dikirim pada status ini",
        )
    order.status = "shipped"
    order.tracking_number = payload.tracking_number
    order.shipped_at = datetime.utcnow()
    db.add(models.OrderStatusHistory(order_id=order.id, status="shipped"))
    db.commit()
    db.refresh(order)
    return _order_out(order)
