from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_pembina_or_admin, get_current_admin

router = APIRouter(prefix="/kompetensi-master", tags=["kompetensi-master"])


def _get_kompetensi_or_404(db: Session, kompetensi_id: int) -> "models.KompetensiMaster":
    from app import models
    kompetensi = db.query(models.KompetensiMaster).filter(models.KompetensiMaster.id == kompetensi_id).first()
    if not kompetensi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kompetensi master tidak ditemukan"
        )
    return kompetensi


@router.get("/", response_model=List[schemas.KompetensiMasterOut])
def list_kompetensi_master(
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    from app import models
    
    query = db.query(models.KompetensiMaster)
    
    # Filter berdasarkan peran
    if current_user.role == "anggota":
        query = query.filter(models.KompetensiMaster.jenjang == current_user.jenjang if hasattr(current_user, 'jenjang') else models.KompetensiMaster.id > 0)
    elif current_user.role == "pembina":
        query = query.filter(models.KompetensiMaster.jenjang == current_user.jenjang if hasattr(current_user, 'jenjang') else models.KompetensiMaster.id > 0)
    
    return query.order_by(models.KompetensiMaster.jenjang, models.KompetensiMaster.jenis).all()


@router.post("/", response_model=schemas.KompetensiMasterOut, status_code=status.HTTP_201_CREATED)
def create_kompetensi_master(
    payload: schemas.KompetensiMasterOut,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    from app import models
    
    existing = (
        db.query(models.KompetensiMaster)
        .filter(
            models.KompetensiMaster.jenis == payload.jenis,
            models.KompetensiMaster.jenjang == payload.jenjang,
            models.KompetensiMaster.nama_kompetensi == payload.nama_kompetensi
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kompetensi master dengan jenis, jenjang, dan nama yang sama sudah ada",
        )

    kompetensi = models.KompetensiMaster(
        jenis=payload.jenis,
        jenjang=payload.jenjang,
        nama_kompetensi=payload.nama_kompetensi,
        tingkat=payload.tingkat,
    )
    db.add(kompetensi)
    db.commit()
    db.refresh(kompetensi)
    return kompetensi


@router.get("/{kompetensi_id}", response_model=schemas.KompetensiMasterOut)
def get_kompetensi_master(
    kompetensi_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    kompetensi = _get_kompetensi_or_404(db, kompetensi_id)
    
    # Data scoping (admin dan pembina bisa melihat semua)
    return kompetensi


@router.put("/{kompetensi_id}", response_model=schemas.KompetensiMasterOut)
def update_kompetensi_master(
    kompetensi_id: int,
    payload: schemas.KompetensiMasterOut,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    kompetensi = _get_kompetensi_or_404(db, kompetensi_id)

    if payload.jenis != kompetensi.jenis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa mengubah jenis kompetensi",
        )

    kompetensicheck = (
        db.query(models.KompetensiMaster)
        .filter(
            models.KompetensiMaster.id != kompetensi_id,
            models.KompetensiMaster.jenis == payload.jenis,
            models.KompetensiMaster.jenjang == payload.jenjang,
            models.KompetensiMaster.nama_kompetensi == payload.nama_kompetensi
        )
        .first()
    )
    if kompetensicheck:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kompetensi master dengan jenis, jenjang, dan nama yang sama sudah ada",
        )

    kompetensi.jenjang = payload.jenjang
    kompetensi.nama_kompetensi = payload.nama_kompetensi
    kompetensi.tingkat = payload.tingkat

    db.commit()
    db.refresh(kompetensi)
    return kompetensi


@router.delete("/{kompetensi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kompetensi_master(
    kompetensi_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    kompetensi = _get_kompetensi_or_404(db, kompetensi_id)
    db.delete(kompetensi)
    db.commit()