from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("", response_model=List[schemas.BadgeOut])
def list_badges(
    level: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(models.Badge).filter(models.Badge.is_active == True)
    if level:
        q = q.filter(models.Badge.level == level)
    if category:
        q = q.filter(models.Badge.category == category)
    return q.order_by(models.Badge.level, models.Badge.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()


@router.get("/{badge_id}", response_model=schemas.BadgeOut)
def get_badge(badge_id: int, db: Session = Depends(get_db)):
    badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge tidak ditemukan")
    return badge


@router.post("", response_model=schemas.BadgeOut, status_code=status.HTTP_201_CREATED)
def create_badge(
    payload: schemas.BadgeCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    existing = db.query(models.Badge).filter(models.Badge.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kode badge sudah ada")
    badge = models.Badge(**payload.model_dump(), created_by=admin.id)
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


@router.put("/{badge_id}", response_model=schemas.BadgeOut)
def update_badge(
    badge_id: int,
    payload: schemas.BadgeUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge tidak ditemukan")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(badge, k, v)
    db.commit()
    db.refresh(badge)
    return badge


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_badge(
    badge_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge tidak ditemukan")
    db.delete(badge)
    db.commit()
