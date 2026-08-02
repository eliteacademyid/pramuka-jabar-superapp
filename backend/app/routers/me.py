from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/me", tags=["me"])


def _get_address_or_404(db: Session, user: models.User, address_id: int) -> models.Address:
    address = (
        db.query(models.Address)
        .filter(models.Address.id == address_id, models.Address.user_id == user.id)
        .first()
    )
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alamat tidak ditemukan"
        )
    return address


@router.put("", response_model=schemas.UserOut)
def update_profile(
    payload: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.nama_lengkap is not None:
        current_user.nama_lengkap = payload.nama_lengkap
    if payload.email is not None:
        current_user.email = payload.email
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/theme", response_model=schemas.ThemeOut)
def get_theme(
    current_user: models.User = Depends(get_current_user),
):
    return {"theme": current_user.theme}


@router.put("/theme", response_model=schemas.ThemeOut)
def update_theme(
    payload: schemas.ThemeUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.theme = payload.theme
    db.commit()
    return {"theme": current_user.theme}


@router.get("/addresses", response_model=List[schemas.AddressOut])
def list_addresses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Address)
        .filter(models.Address.user_id == current_user.id)
        .order_by(models.Address.is_primary.desc(), models.Address.id)
        .all()
    )


@router.post("/addresses", response_model=schemas.AddressOut, status_code=status.HTTP_201_CREATED)
def create_address(
    payload: schemas.AddressCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.is_primary:
        db.query(models.Address).filter(models.Address.user_id == current_user.id).update(
            {models.Address.is_primary: False}
        )
    address = models.Address(user_id=current_user.id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/addresses/{address_id}", response_model=schemas.AddressOut)
def update_address(
    address_id: int,
    payload: schemas.AddressUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = _get_address_or_404(db, current_user, address_id)
    if payload.is_primary:
        db.query(models.Address).filter(models.Address.user_id == current_user.id).update(
            {models.Address.is_primary: False}
        )
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, field, value)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    address = _get_address_or_404(db, current_user, address_id)
    db.delete(address)
    db.commit()
