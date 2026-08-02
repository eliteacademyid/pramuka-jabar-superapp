from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_pembina_or_admin

router = APIRouter(tags=["referensi"])


@router.get("/wilayah", response_model=List[schemas.WilayahOut])
def list_wilayah(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Wilayah).order_by(models.Wilayah.id).all()


@router.post("/wilayah", response_model=schemas.WilayahOut, status_code=status.HTTP_201_CREATED)
def create_wilayah(
    payload: schemas.WilayahCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_pembina_or_admin),
):
    existing = (
        db.query(models.Wilayah)
        .filter(models.Wilayah.nama == payload.nama, models.Wilayah.tingkat == payload.tingkat)
        .first()
    )
    if existing:
        return existing

    wilayah = models.Wilayah(
        nama=payload.nama,
        tingkat=payload.tingkat,
        parent_id=payload.parent_id,
    )
    db.add(wilayah)
    db.commit()
    db.refresh(wilayah)
    return wilayah


@router.get("/gudep", response_model=List[schemas.GudepOut])
def list_gudep(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    return db.query(models.Gudep).order_by(models.Gudep.id).all()


@router.post("/gudep", response_model=schemas.GudepOut, status_code=status.HTTP_201_CREATED)
def create_gudep(
    payload: schemas.GudepCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_pembina_or_admin),
):
    existing = db.query(models.Gudep).filter(models.Gudep.nama == payload.nama).first()
    if existing:
        return existing

    wilayah = None
    if payload.wilayah_id:
        wilayah = db.query(models.Wilayah).filter(models.Wilayah.id == payload.wilayah_id).first()
        if not wilayah:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wilayah tidak ditemukan"
            )
    else:
        wilayah = (
            db.query(models.Wilayah)
            .filter(models.Wilayah.tingkat == "Kwartir Cabang")
            .first()
        )
    if not wilayah:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak ada wilayah yang bisa dipakai untuk gudep",
        )

    gudep = models.Gudep(
        nama=payload.nama,
        pangkalan=payload.pangkalan,
        wilayah_id=wilayah.id,
    )
    db.add(gudep)
    db.commit()
    db.refresh(gudep)
    return gudep
