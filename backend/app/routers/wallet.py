from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_active_store, get_current_admin, get_current_user
from app.services.common import ensure_wallet
from app.services.wallet_service import (
    approve_withdraw,
    reject_withdraw,
    request_withdraw,
    topup,
)

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=schemas.WalletDetailOut)
def get_wallet(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = ensure_wallet(db, current_user)
    db.commit()
    txs = (
        db.query(models.WalletTransaction)
        .filter(models.WalletTransaction.wallet_id == wallet.id)
        .order_by(models.WalletTransaction.created_at.desc())
        .all()
    )
    return schemas.WalletDetailOut(
        wallet=schemas.WalletOut(
            id=wallet.id, balance=wallet.balance, escrow_balance=wallet.escrow_balance
        ),
        transactions=[schemas.WalletTxOut.model_validate(tx) for tx in txs],
    )


@router.post("/topup", response_model=schemas.WalletDetailOut)
def topup_endpoint(
    payload: schemas.TopupRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = topup(db, current_user, payload.amount)
    db.commit()
    txs = (
        db.query(models.WalletTransaction)
        .filter(models.WalletTransaction.wallet_id == wallet.id)
        .order_by(models.WalletTransaction.created_at.desc())
        .all()
    )
    return schemas.WalletDetailOut(
        wallet=schemas.WalletOut(
            id=wallet.id, balance=wallet.balance, escrow_balance=wallet.escrow_balance
        ),
        transactions=[schemas.WalletTxOut.model_validate(tx) for tx in txs],
    )


@router.post("/withdrawals", response_model=schemas.WithdrawalOut, status_code=status.HTTP_201_CREATED)
def withdraw_endpoint(
    payload: schemas.WithdrawRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    withdrawal = request_withdraw(
        db,
        current_user,
        payload.amount,
        payload.bank_name,
        payload.account_number,
        payload.account_name,
    )
    db.commit()
    db.refresh(withdrawal)
    return withdrawal


@router.get("/seller/withdrawals", response_model=List[schemas.WithdrawalOut])
def list_my_withdrawals(
    store: models.Store = Depends(get_active_store),
    db: Session = Depends(get_db),
):
    withdrawals = (
        db.query(models.Withdrawal)
        .filter(models.Withdrawal.user_id == store.owner_id)
        .order_by(models.Withdrawal.created_at.desc())
        .all()
    )
    return withdrawals


@router.get("/withdrawals", response_model=List[schemas.WithdrawalOut])
def list_my_withdrawals_general(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    withdrawals = (
        db.query(models.Withdrawal)
        .filter(models.Withdrawal.user_id == current_user.id)
        .order_by(models.Withdrawal.created_at.desc())
        .all()
    )
    return withdrawals


admin_router = APIRouter(prefix="/admin/withdrawals", tags=["admin"])


def _withdrawal_or_404(db: Session, withdrawal_id: int) -> models.Withdrawal:
    withdrawal = db.get(models.Withdrawal, withdrawal_id)
    if not withdrawal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pengajuan tidak ditemukan"
        )
    return withdrawal


@admin_router.get("", response_model=List[schemas.WithdrawalOut])
def admin_list_withdrawals(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return (
        db.query(models.Withdrawal)
        .order_by(models.Withdrawal.created_at.desc())
        .all()
    )


@admin_router.post("/{withdrawal_id}/approve", response_model=schemas.WithdrawalOut)
def admin_approve_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    withdrawal = _withdrawal_or_404(db, withdrawal_id)
    if withdrawal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Pengajuan sudah diproses"
        )
    approve_withdraw(db, withdrawal)
    db.commit()
    db.refresh(withdrawal)
    return withdrawal


@admin_router.post("/{withdrawal_id}/reject", response_model=schemas.WithdrawalOut)
def admin_reject_withdrawal(
    withdrawal_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    withdrawal = _withdrawal_or_404(db, withdrawal_id)
    if withdrawal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Pengajuan sudah diproses"
        )
    reject_withdraw(db, withdrawal)
    db.commit()
    db.refresh(withdrawal)
    return withdrawal
