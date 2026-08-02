from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(tags=["referensi"])


@router.get("/wilayah", response_model=List[schemas.WilayahOut])
def list_wilayah(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Wilayah).order_by(models.Wilayah.id).all()


@router.get("/gudep", response_model=List[schemas.GudepOut])
def list_gudep(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Gudep).order_by(models.Gudep.id).all()
