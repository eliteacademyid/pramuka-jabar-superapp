import random
import re
import string

from sqlalchemy.orm import Session

from app import models


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "item"


def unique_slug(db: Session, model, name: str) -> str:
    """Buat slug unik dari name; bila bentrok tambahkan suffix numerik (R-203/E-06)."""
    base = slugify(name)
    candidate = base
    counter = 2
    while db.query(model).filter(model.slug == candidate).first():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def generate_order_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "ORD-" + "".join(random.choices(alphabet, k=8))


def ensure_wallet(db: Session, user: models.User) -> models.Wallet:
    """Pastikan user punya wallet; buat jika belum (R-109)."""
    wallet = db.query(models.Wallet).filter(models.Wallet.user_id == user.id).first()
    if not wallet:
        wallet = models.Wallet(user_id=user.id, balance=0, escrow_balance=0)
        db.add(wallet)
        db.flush()
    return wallet


def get_setting(db: Session, key: str, default: str = "") -> str:
    row = db.query(models.Setting).filter(models.Setting.key == key).first()
    if row is None:
        db.add(models.Setting(key=key, value=default))
        db.flush()
        return default
    return row.value


def record_wallet_tx(
    db: Session,
    wallet: models.Wallet,
    tx_type: str,
    amount,
    balance_after,
    ref_type: str | None = None,
    ref_id: int | None = None,
    note: str | None = None,
) -> models.WalletTransaction:
    tx = models.WalletTransaction(
        wallet_id=wallet.id,
        type=tx_type,
        amount=amount,
        ref_type=ref_type,
        ref_id=ref_id,
        balance_after=balance_after,
        note=note,
    )
    db.add(tx)
    return tx


def record_order_status(
    db: Session, order: models.Order, status: str, note: str | None = None
) -> None:
    db.add(
        models.OrderStatusHistory(order_id=order.id, status=status, note=note)
    )
