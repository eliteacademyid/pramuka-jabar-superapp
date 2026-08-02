from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user, get_current_pembina_or_admin, get_current_admin

router = APIRouter(prefix="/anggota", tags=["anggota"])


def _get_anggota_or_404(db: Session, anggota_id: int) -> "models.Anggota":
    from app import models
    anggota = db.query(models.Anggota).filter(models.Anggota.id == anggota_id).first()
    if not anggota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anggota tidak ditemukan"
        )
    return anggota


@router.post("/", response_model=schemas.AnggotaOut, status_code=status.HTTP_201_CREATED)
def create_anggota(
    payload: schemas.AnggotaCreate,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    from app import models
    
    existing = (
        db.query(models.Anggota)
        .filter(models.Anggota.nta == payload.nta)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NTA sudah digunakan",
        )

    # Check scope
    if current_user.role == "anggota":
        if payload.gudep_id != current_user.gudep_scope:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa membuat anggota di gudep lain",
            )
    
    # Check if gudep exists
    gudep = db.query(models.Gudep).filter(models.Gudep.id == payload.gudep_id).first()
    if not gudep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gudep tidak ditemukan",
        )

    anggota = models.Anggota(
        nta=payload.nta,
        nama_lengkap=payload.nama_lengkap,
        tanggal_lahir=payload.tanggal_lahir,
        jenis_kelamin=payload.jenis_kelamin,
        jenjang=payload.jenjang,
        alamat=payload.alamat,
        status_aktif=payload.status_aktif,
        gudep_id=payload.gudep_id,
    )
    db.add(anggota)
    db.commit()
    db.refresh(anggota)
    return anggota


@router.get("/", response_model=List[schemas.AnggotaOut])
def list_anggota(
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    from app import models
    
    query = db.query(models.Anggota)
    
    # Apply data scoping
    if current_user.role == "anggota":
        query = query.filter(models.Anggota.user_id == current_user.id)
    elif current_user.role == "pembina":
        query = query.filter(models.Anggota.user_id == current_user.id)
    elif current_user.role in ("admin_gudep", "admin_kwarcab"):
        if current_user.wilayah_scope_id:
            query = query.join(models.Gudep).filter(models.Gudep.wilayah_id == current_user.wilayah_scope_id)
        if current_user.gudep_scope_id:
            query = query.filter(models.Anggota.gudep_id == current_user.gudep_scope_id)
    
    # Apply filters
    # (Can be extended with query params)
    
    return query.order_by(models.Anggota.id).all()


@router.get("/{anggota_id}", response_model=schemas.AnggotaOut)
def get_anggota(
    anggota_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    anggota = _get_anggota_or_404(db, anggota_id)
    
    # Apply data scoping
    if current_user.role == "anggota":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses data anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses data anggota lain",
            )
    elif current_user.role == "admin_gudep":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses data anggota di gudep lain",
            )
    elif current_user.role == "admin_kwarcab":
        gudep = db.query(models.Gudep).filter(models.Gudep.id == anggota.gudep_id).first()
        if gudep and gudep.wilayah_id != current_user.wilayah_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses data anggota di wilayah lain",
            )
    
    return anggota


@router.put("/{anggota_id}", response_model=schemas.AnggotaOut)
def update_anggota(
    anggota_id: int,
    payload: schemas.AnggotaCreate,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    anggota = _get_anggota_or_404(db, anggota_id)
    
    # Apply data scoping
    if current_user.role == "anggota":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengubah data anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengubah data anggota lain",
            )
    elif current_user.role == "admin_gudep":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengubah data anggota di gudep lain",
            )
    
    # Check NTA uniqueness if changed
    if payload.nta != anggota.nta:
        existing = (
            db.query(models.Anggota)
            .filter(models.Anggota.nta == payload.nta)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NTA sudah digunakan",
            )
        anggota.nta = payload.nta
    
    anggota.nama_lengkap = payload.nama_lengkap
    anggota.tanggal_lahir = payload.tanggal_lahir
    anggota.jenis_kelamin = payload.jenis_kelamin
    anggota.jenjang = payload.jenjang
    anggota.alamat = payload.alamat
    anggota.status_aktif = payload.status_aktif
    
    # Check gudep scope
    if current_user.role in ("admin_gudep", "pembina"):
        # Pembina hanya bisa mengubah anggota di gudepnya
        gudep = db.query(models.Gudep).filter(models.Gudep.id == payload.gudep_id).first()
        if gudep and gudep.wilayah_id != current_user.wilayah_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengubah gudep di wilayah lain",
            )
    
    anggota.gudep_id = payload.gudep_id

    db.commit()
    db.refresh(anggota)
    return anggota


@router.delete("/{anggota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anggota(
    anggota_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_admin),
):
    anggota = _get_anggota_or_404(db, anggota_id)
    
    # Only admin can delete
    db.delete(anggota)
    db.commit()