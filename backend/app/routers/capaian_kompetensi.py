from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.deps import get_current_user, get_current_admin, get_current_pembina_or_admin

router = APIRouter(prefix="/capaian-kompetensi", tags=["capaian-kompetensi"])


def _get_capaian_or_404(db: Session, capaian_id: int) -> "models.CapaianKompetensi":
    from app import models
    capaian = db.query(models.CapaianKompetensi).filter(models.CapaianKompetensi.id == capaian_id).first()
    if not capaian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Capaian kompetensi tidak ditemukan"
        )
    return capaian


@router.post("/", response_model=schemas.CapaianKompetensiOut, status_code=status.HTTP_201_CREATED)
def create_capaian_kompetensi(
    payload: schemas.CapaianKompetensiCreate,
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
                detail="Tidak bisa mencatat capaian kompetensi anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mencatat capaian kompetensi anggota di gudep lain",
            )
    
    # Verifikasi kompetensi master exist dan sesuai jenjang
    kompetensi = db.query(models.KompetensiMaster).filter(
        models.KompetensiMaster.id == payload.kompetensi_id
    ).first()
    if not kompetensi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kompetensi master tidak ditemukan",
        )
    
    if kompetensi.jenjang != anggota.jenjang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kompetensi tidak sesuai dengan jenjang anggota",
        )
    
    # Verifikasi penguji adalah Pembina atau anggota
    penguji = db.query(models.Anggota).filter(models.Anggota.id == payload.penguji_id).first()
    if not penguji:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Penguji tidak ditemukan",
        )
    
    # Jika penguji adalah anggota biasa, hanya bisa mencatat capaian untuk dirinya sendiri
    if penguji.role == "anggota":
        if penguji.id != payload.anggota_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Anggota hanya bisa mencatat capaian untuk dirinya sendiri",
            )
    
    capaian = models.CapaianKompetensi(
        anggota_id=payload.anggota_id,
        kompetensi_id=payload.kompetensi_id,
        tanggal_capai=payload.tanggal_capai or datetime.utcnow(),
        penguji_id=payload.penguji_id,
    )
    db.add(capaian)
    db.commit()
    db.refresh(capaian)
    return capaian


@router.get("/", response_model=List[schemas.CapaianKompetensiOut])
def list_capaian_kompetensi(
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
    filter: Optional[schemas.CapaianKompetensiFilter] = None,
):
    from app import models
    
    query = db.query(models.CapaianKompetensi)
    
    # Apply data scoping
    if current_user.role == "anggota":
        query = query.join(models.Anggota).filter(models.Anggota.user_id == current_user.id)
    elif current_user.role == "pembina":
        query = query.join(models.Anggota).filter(models.Anggota.gudep_id == current_user.gudep_scope_id)
    
    # Apply filters
    if filter:
        if filter.anggota_id:
            query = query.filter(models.CapaianKompetensi.anggota_id == filter.anggota_id)
        if filter.kompetensi_id:
            query = query.filter(models.CapaianKompetensi.kompetensi_id == filter.kompetensi_id)
        if filter.jenjang:
            # Join with anggota table to filter by jenjang
            query = query.join(models.Anggota).filter(models.Anggota.jenjang == filter.jenjang)
    
    return query.order_by(models.CapaianKompetensi.tanggal_capai.desc()).all()


@router.get("/anggota/{anggota_id}", response_model=List[schemas.CapaianKompetensiOut])
def list_capaian_anggota(
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
                detail="Tidak bisa mengakses capaian anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses capaian anggota di gudep lain",
            )
    
    return anggota.capaian_kompetensi


@router.get("/{capaian_id}", response_model=schemas.CapaianKompetensiOut)
def get_capaian_kompetensi(
    capaian_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    capaian = _get_capaian_or_404(db, capaian_id)
    
    # Apply data scoping
    anggota = capaian.anggota
    if current_user.role == "anggota":
        if anggota.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses capaian kompetensi anggota lain",
            )
    elif current_user.role == "pembina":
        if anggota.gudep_id != current_user.gudep_scope_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tidak bisa mengakses capaian kompetensi anggota di gudep lain",
            )
    
    return capaian


@router.put("/{capaian_id}", response_model=schemas.CapaianKompetensiOut)
def update_capaian_kompetensi(
    capaian_id: int,
    payload: schemas.CapaianKompetensiCreate,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_user),
):
    capaian = _get_capaian_or_404(db, capaian_id)
    
    # Apply data scoping - hanya pembina bisa mengubah
    if current_user.role != "pembina":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya pembina yang bisa mengubah capaian kompetensi",
        )
    
    anggota = capaian.anggota
    if anggota.gudep_id != current_user.gudep_scope_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tidak bisa mengubah capaian anggota di gudep lain",
        )

    capaian.anggota_id = payload.anggota_id
    capaian.kompetensi_id = payload.kompetensi_id
    if payload.tanggal_capai:
        capaian.tanggal_capai = payload.tanggal_capai
    capaian.penguji_id = payload.penguji_id

    db.commit()
    db.refresh(capaian)
    return capaian


@router.delete("/{capaian_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_capaian_kompetensi(
    capaian_id: int,
    db: Session = Depends(get_db),
    current_user: "models.User" = Depends(get_current_admin),
):
    capaian = _get_capaian_or_404(db, capaian_id)
    db.delete(capaian)
    db.commit()