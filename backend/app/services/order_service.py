from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session

from app import models
from app.services.common import (
    generate_order_code,
    get_setting,
    record_order_status,
)
from app.services.wallet_service import refund_order, release_escrow


def _shipping_fee_tier(store: models.Store, city: str, province: str) -> str:
    if store.city == city:
        return "ONGKIR_TIER_A"
    if store.province == province:
        return "ONGKIR_TIER_B"
    return "ONGKIR_TIER_C"


def _shipping_fee(db: Session, store: models.Store, city: str, province: str) -> Decimal:
    """Mock ongkir tier (R-307): kota sama / provinsi sama / beda provinsi."""
    key = _shipping_fee_tier(store, city, province)
    return Decimal(get_setting(db, key, "10000")).quantize(Decimal("0.01"))


def checkout(db: Session, user: models.User, address_id: int) -> list[str]:
    """Checkout atomic: order per toko, validasi stok FOR UPDATE, stok berkurang,
    keranjang dibersihkan (R-304..R-307, E-01, E-02, E-09)."""
    address = (
        db.query(models.Address)
        .filter(models.Address.id == address_id, models.Address.user_id == user.id)
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Pilih alamat pengiriman terlebih dahulu",
        )

    cart_items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == user.id)
        .all()
    )
    if not cart_items:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, detail="Keranjang kosong"
        )

    grouped: dict[int, list[models.CartItem]] = {}
    product_ids = []
    for item in cart_items:
        grouped.setdefault(item.product.store_id, []).append(item)
        product_ids.append(item.product_id)

    products = (
        db.query(models.Product)
        .filter(models.Product.id.in_(product_ids))
        .with_for_update()
        .all()
    )
    product_map = {p.id: p for p in products}

    address_snapshot = {
        "label": address.label,
        "address_line": address.address_line,
        "city": address.city,
        "province": address.province,
        "postal_code": address.postal_code,
        "phone": address.phone,
    }

    order_codes: list[str] = []

    for store_id, items in grouped.items():
        store = db.get(models.Store, store_id)
        subtotal = Decimal("0.00")
        order_items = []
        for item in items:
            product = product_map[item.product_id]
            if product.status != "active" or store.status != "active":
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="Produk tidak tersedia",
                )
            if product.stock < item.qty:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Stok produk {product.name} tidak mencukupi",
                )
            line_total = Decimal(product.price) * item.qty
            subtotal += line_total
            order_items.append(
                models.OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    unit_price=Decimal(product.price),
                    qty=item.qty,
                    total=line_total,
                )
            )

        shipping = _shipping_fee(db, store, address.city, address.province)
        order = models.Order(
            order_code=generate_order_code(),
            buyer_id=user.id,
            store_id=store_id,
            address_snapshot=address_snapshot,
            subtotal=subtotal,
            shipping_fee=shipping,
            discount=Decimal("0.00"),
            total=subtotal + shipping,
            status="pending_payment",
            escrow_status="none",
            items=order_items,
        )
        db.add(order)
        db.flush()
        db.add(models.Conversation(order_id=order.id))
        record_order_status(
            db,
            order,
            "pending_payment",
            note=f"Ongkir: {_shipping_fee_tier(store, address.city, address.province)}",
        )
        order_codes.append(order.order_code)

        for item in items:
            product = product_map[item.product_id]
            product.stock -= item.qty
            product.sold += item.qty

    for item in cart_items:
        db.delete(item)

    return order_codes


def cancel_order(db: Session, order: models.Order) -> None:
    """Batalkan order: hanya pending_payment/paid; jika paid -> refund (R-312, E-13)."""
    if order.status not in ("pending_payment", "paid"):
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Order tidak dapat dibatalkan pada status ini",
        )
    if order.status == "paid":
        refund_order(db, order)
    else:
        order.status = "cancelled"
        record_order_status(db, order, "cancelled", note="Dibatalkan pembeli")


def confirm_receipt(db: Session, order: models.Order) -> None:
    """Konfirmasi terima: shipped -> delivered -> completed + release escrow (R-311)."""
    if order.status != "shipped":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Order belum dikirim, tidak dapat dikonfirmasi",
        )
    order.status = "delivered"
    record_order_status(db, order, "delivered", note="Barang diterima pembeli")
    order.status = "completed"
    record_order_status(db, order, "completed")
    release_escrow(db, order)
