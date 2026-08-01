from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/tkk", tags=["tkk"])


@router.get("", response_model=List[schemas.TKKOut])
def list_tkk(
    bidang: Optional[str] = None,
    level: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(models.TKK).filter(models.TKK.is_active == True)
    if bidang:
        q = q.filter(models.TKK.bidang == bidang)
    if level:
        q = q.filter(models.TKK.level == level)
    if category:
        q = q.filter(models.TKK.category == category)
    return q.order_by(models.TKK.bidang, models.TKK.level).offset(
        (page - 1) * limit
    ).limit(limit).all()


@router.get("/bidang/{bidang}", response_model=List[schemas.TKKOut])
def get_tkk_by_bidang(bidang: str, db: Session = Depends(get_db)):
    return (
        db.query(models.TKK)
        .filter(models.TKK.bidang == bidang, models.TKK.is_active == True)
        .order_by(models.TKK.level)
        .all()
    )


@router.get("/{tkk_id}", response_model=schemas.TKKOut)
def get_tkk(tkk_id: int, db: Session = Depends(get_db)):
    tkk = db.query(models.TKK).filter(models.TKK.id == tkk_id).first()
    if not tkk:
        raise HTTPException(status_code=404, detail="TKK tidak ditemukan")
    return tkk


@router.post("", response_model=schemas.TKKOut, status_code=status.HTTP_201_CREATED)
def create_tkk(
    payload: schemas.TKKCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    existing = db.query(models.TKK).filter(models.TKK.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kode TKK sudah ada")
    tkk = models.TKK(**payload.model_dump(), created_by=admin.id)
    db.add(tkk)
    db.commit()
    db.refresh(tkk)
    return tkk


@router.put("/{tkk_id}", response_model=schemas.TKKOut)
def update_tkk(
    tkk_id: int,
    payload: schemas.TKKUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    tkk = db.query(models.TKK).filter(models.TKK.id == tkk_id).first()
    if not tkk:
        raise HTTPException(status_code=404, detail="TKK tidak ditemukan")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tkk, k, v)
    db.commit()
    db.refresh(tkk)
    return tkk


@router.delete("/{tkk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tkk(
    tkk_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    tkk = db.query(models.TKK).filter(models.TKK.id == tkk_id).first()
    if not tkk:
        raise HTTPException(status_code=404, detail="TKK tidak ditemukan")
    db.delete(tkk)
    db.commit()
