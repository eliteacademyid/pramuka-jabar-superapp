from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("", response_model=List[schemas.AchievementOut])
def list_achievements(
    achievement_type: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(models.Achievement).filter(models.Achievement.is_active == True)
    if achievement_type:
        q = q.filter(models.Achievement.achievement_type == achievement_type)
    if category:
        q = q.filter(models.Achievement.category == category)
    if level:
        q = q.filter(models.Achievement.level == level)
    return q.order_by(models.Achievement.level, models.Achievement.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()


@router.get("/category/{category}", response_model=List[schemas.AchievementOut])
def get_achievements_by_category(category: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Achievement)
        .filter(models.Achievement.category == category, models.Achievement.is_active == True)
        .order_by(models.Achievement.level)
        .all()
    )


@router.get("/{ach_id}", response_model=schemas.AchievementOut)
def get_achievement(ach_id: int, db: Session = Depends(get_db)):
    ach = db.query(models.Achievement).filter(models.Achievement.id == ach_id).first()
    if not ach:
        raise HTTPException(status_code=404, detail="Prestasi tidak ditemukan")
    return ach


@router.post("", response_model=schemas.AchievementOut, status_code=status.HTTP_201_CREATED)
def create_achievement(
    payload: schemas.AchievementCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    existing = db.query(models.Achievement).filter(models.Achievement.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kode prestasi sudah ada")
    ach = models.Achievement(**payload.model_dump(), created_by=admin.id)
    db.add(ach)
    db.commit()
    db.refresh(ach)
    return ach


@router.put("/{ach_id}", response_model=schemas.AchievementOut)
def update_achievement(
    ach_id: int,
    payload: schemas.AchievementUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    ach = db.query(models.Achievement).filter(models.Achievement.id == ach_id).first()
    if not ach:
        raise HTTPException(status_code=404, detail="Prestasi tidak ditemukan")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(ach, k, v)
    db.commit()
    db.refresh(ach)
    return ach


@router.delete("/{ach_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_achievement(
    ach_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    ach = db.query(models.Achievement).filter(models.Achievement.id == ach_id).first()
    if not ach:
        raise HTTPException(status_code=404, detail="Prestasi tidak ditemukan")
    db.delete(ach)
    db.commit()
