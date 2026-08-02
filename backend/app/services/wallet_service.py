from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status as http_status
from sqlalchemy.orm import Session

from app import models
from app.services.common import (
    ensure_wallet,
    get_setting,
    record_order_status,
    record_wallet_tx,
)
from app.services.notify import notify


def _lock_wallet(db: Session, user_id: int) -> models.Wallet:
    wallet = (
        db.query(models.Wallet)
        .filter(models.Wallet.user_id == user_id)
        .with_for_update()
        .first()
    )
    if not wallet:
        wallet = ensure_wallet(db, db.query(models.User).get(user_id))
        wallet = (
            db.query(models.Wallet)
            .filter(models.Wallet.user_id == user_id)
            .with_for_update()
            .first()
        )
    return wallet


def topup(db: Session, user: models.User, amount: Decimal) -> models.Wallet:
    wallet = _lock_wallet(db, user.id)
    wallet.balance = Decimal(wallet.balance) + amount
    record_wallet_tx(
        db, wallet, "topup", amount, wallet.balance, note="Top-up saldo (mock payment)"
    )
    return wallet


def pay_order(db: Session, order: models.Order) -> None:
    """Bayar order dari wallet pembeli -> escrow (R-402, R-403, E-03). Atomic."""
    if order.status != "pending_payment":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, detail="Order sudah dibayar"
        )

    wallet = _lock_wallet(db, order.buyer_id)
    total = Decimal(order.total)
    if Decimal(wallet.balance) < total:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Saldo tidak mencukupi",
        )

    wallet.balance = Decimal(wallet.balance) - total
    wallet.escrow_balance = Decimal(wallet.escrow_balance) + total

    order.status = "paid"
    order.escrow_status = "held"
    order.paid_at = datetime.utcnow()
    order.commission_rate = Decimal(get_setting(db, "COMMISSION_RATE", "5") or "5")

    notify(
        db,
        order.store.owner_id,
        "order",
        "Pesanan dibayar",
        f"Pesanan {order.order_code} sudah dibayar pembeli — siap diproses.",
        "/account/seller/orders",
    )

    record_wallet_tx(
        db,
        wallet,
        "payment",
        -total,
        wallet.balance,
        ref_type="order",
        ref_id=order.id,
        note=f"Pembayaran order {order.order_code}",
    )
    record_order_status(db, order, "paid")


def release_escrow(db: Session, order: models.Order) -> None:
    """Saat order completed: escrow pembeli dilepas ke penjual dikurangi komisi (R-404)."""
    buyer_wallet = _lock_wallet(db, order.buyer_id)
    total = Decimal(order.total)
    rate = Decimal(order.commission_rate or get_setting(db, "COMMISSION_RATE", "5"))
    commission = (total * rate / Decimal(100)).quantize(Decimal("0.01"))
    net = total - commission

    buyer_wallet.escrow_balance = Decimal(buyer_wallet.escrow_balance) - total
    record_wallet_tx(
        db,
        buyer_wallet,
        "escrow_release",
        -total,
        buyer_wallet.balance,
        ref_type="order",
        ref_id=order.id,
        note=f"Escrow order {order.order_code} dilepas",
    )

    seller_wallet = _lock_wallet(db, order.store.owner_id)
    seller_wallet.balance = Decimal(seller_wallet.balance) + net
    record_wallet_tx(
        db,
        seller_wallet,
        "escrow_release",
        net,
        seller_wallet.balance,
        ref_type="order",
        ref_id=order.id,
        note=f"Hasil penjualan order {order.order_code}",
    )
    record_wallet_tx(
        db,
        seller_wallet,
        "commission",
        commission,
        seller_wallet.balance,
        ref_type="order",
        ref_id=order.id,
        note=f"Komisi platform {rate}% order {order.order_code}",
    )

    order.escrow_status = "released"
    order.completed_at = datetime.utcnow()


def refund_order(db: Session, order: models.Order) -> None:
    """Refund penuh ke pembeli saat order paid dibatalkan (R-312, R-406)."""
    wallet = _lock_wallet(db, order.buyer_id)
    total = Decimal(order.total)
    wallet.escrow_balance = Decimal(wallet.escrow_balance) - total
    wallet.balance = Decimal(wallet.balance) + total
    record_wallet_tx(
        db,
        wallet,
        "refund",
        total,
        wallet.balance,
        ref_type="order",
        ref_id=order.id,
        note=f"Refund order {order.order_code}",
    )
    order.status = "refunded"
    order.escrow_status = "refunded"
    record_order_status(db, order, "refunded", note="Dana dikembalikan ke pembeli")


def request_withdraw(
    db: Session,
    user: models.User,
    amount: Decimal,
    bank_name: str,
    account_number: str,
    account_name: str,
) -> models.Withdrawal:
    wallet = _lock_wallet(db, user.id)
    if Decimal(wallet.balance) < amount:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Saldo tidak mencukupi",
        )
    wallet.balance = Decimal(wallet.balance) - amount
    record_wallet_tx(
        db,
        wallet,
        "withdraw_hold",
        -amount,
        wallet.balance,
        ref_type="withdraw",
        note="Dana pencairan ditahan",
    )
    withdrawal = models.Withdrawal(
        user_id=user.id,
        amount=amount,
        bank_name=bank_name,
        account_number=account_number,
        account_name=account_name,
        status="pending",
    )
    db.add(withdrawal)
    db.flush()
    return withdrawal


def approve_withdraw(db: Session, withdrawal: models.Withdrawal) -> None:
    withdrawal.status = "processed"
    withdrawal.processed_at = datetime.utcnow()


def reject_withdraw(db: Session, withdrawal: models.Withdrawal) -> None:
    wallet = _lock_wallet(db, withdrawal.user_id)
    amount = Decimal(withdrawal.amount)
    wallet.balance = Decimal(wallet.balance) + amount
    record_wallet_tx(
        db,
        wallet,
        "withdraw_reject",
        amount,
        wallet.balance,
        ref_type="withdraw",
        ref_id=withdrawal.id,
        note="Pencairan ditolak, dana dikembalikan",
    )
    withdrawal.status = "rejected"
    withdrawal.processed_at = datetime.utcnow()
