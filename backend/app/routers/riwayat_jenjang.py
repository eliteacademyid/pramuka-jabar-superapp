from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user, get_current_pembina_or_admin, get_current_admin

router = APIRouter(prefix="/riwayat-jenjang", tags=["riwayat-jenjang"])


def _get_riwayat_jenjang_or_404(db: Session, riwayat_id: int) -> "models.RiwayatJenjang":
    from app import models
    riwayat = db.query(models.RiwayatJenjang).filter(models.RiwayatJenjang.id == riwayat_id).first()
    if not riwayat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Riwayat jenjang tidak ditemukan"
        )
    return riwayat


@router.post("/", response_model=schemas.RiwayatJenjangOut, status_code=status.HTTP_201_CREATED)
def create_riwayat_jenjang(
    payload: schemas.RiwayatJenjangCreate,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    from app import models
    from datetime import datetime
    
    anggota = db.query(models.Anggota).filter(models.Anggota.id == payload.anggota_id).first()
    if not anggota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anggota tidak ditemukan",
        )
    
    # Apply data scoping
    if current_user.role == "anggota":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mencatat riwayat jenjang anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mencatat riwayat jenjang anggota di gudep lain",
            )

    riwayat = models.RiwayatJenjang(
        anggota_id=payload.anggota_id,
        jenjang_lama=payload.jenjang_lama,
        jenjang_baru=payload.jenjang_baru,
        tanggal_mutasi=payload.tanggal_mutasi or datetime.utcnow(),
    )
    db.add(riwayat)
    db.commit()
    db.refresh(riwayat)
    return riwayat


@router.get("/anggota/{anggota_id}", response_model=List[schemas.RiwayatJenjangOut])
def list_riwayat_jenjang_anggota(
    anggota_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    from app import models
    
    anggota = db.query(models.Anggota).filter(models.Anggota.id == anggota_id).first()
    if not anggota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anggota tidak ditemukan",
        )
    
    # Apply data scoping
    if current_user.role == "anggota":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses riwayat anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses riwayat anggota di gudep lain",
            )
    
    return anggota.riwayat_jenjang


@router.get("/{riwayat_id}", response_model=schemas.RiwayatJenjangOut)
def get_riwayat_jenjang(
    riwayat_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    riwayat = _get_riwayat_jenjang_or_404(db, riwayat_id)
    
    # Apply data scoping
    anggota = riwayat.anggota
    if current_user.role == "anggota":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses riwayat jenjang anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses riwayat jenjang anggota di gudep lain",
            )
    
    return riwayat


@router.put("/{riwayat_id}", response_model=schemas.RiwayatJenjangOut)
def update_riwayat_jenjang(
    riwayat_id: int,
    payload: schemas.RiwayatJenjangCreate,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    from app import models
    
    riwayat = _get_riwayat_jenjang_or_404(db, riwayat_id)
    
    # Apply data scoping
    anggota = riwayat.anggota
    if current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengubah riwayat jenjang anggota di gudep lain",
            )

    anggota = db.query(models.Anggota).filter(models.Anggota.id == payload.anggota_id).first()
    if not anggota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anggota tidak ditemukan",
        )
    
    # Check pembina scope
    if current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengubah anggota di gudep lain",
            )

    riwayat.anggota_id = payload.anggota_id
    riwayat.jenjang_lama = payload.jenjang_lama
    riwayat.jenjang_baru = payload.jenjang_baru
    if payload.tanggal_mutasi:
        riwayat.tanggal_mutasi = payload.tanggal_mutasi

    db.commit()
    db.refresh(riwayat)
    return riwayat


@router.delete("/{riwayat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_riwayat_jenjang(
    riwayat_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_admin),
):
    riwayat = _get_riwayat_jenjang_or_404(db, riwayat_id)
    db.delete(riwayat)
    db.commit()