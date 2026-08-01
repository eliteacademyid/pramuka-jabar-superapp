from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/organisasi", tags=["Organisasi"])


@router.get("", response_model=List[schemas.OrganisasiResponse])
def get_all_organisasi(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """Get all organisasi with optional search and active filter."""
    query = db.query(models.Organisasi)

    if search:
        query = query.filter(models.Organisasi.nama.ilike(f"%{search}%"))

    if is_active is not None:
        query = query.filter(models.Organisasi.is_active == is_active)

    # created_at kini punya index — ORDER BY tetap cepat
    return query.order_by(models.Organisasi.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{organisasi_id}", response_model=schemas.OrganisasiResponse)
def get_organisasi_by_id(organisasi_id: int, db: Session = Depends(get_db)):
    """Get organisasi by ID."""
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id
    ).first()

    if not organisasi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan",
        )

    return organisasi


@router.post("", response_model=schemas.OrganisasiResponse, status_code=status.HTTP_201_CREATED)
def create_organisasi(
    organisasi_data: schemas.OrganisasiCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Create new organisasi (admin only)."""
    # EXISTS lebih ringan dari SELECT * — tidak fetch semua kolom
    # nama sudah unique=True di DB sehingga INSERT akan gagal jika duplikat,
    # tapi cek lebih awal memberi pesan error yang lebih jelas.
    nama_exists = db.query(
        db.query(models.Organisasi).filter(models.Organisasi.nama == organisasi_data.nama).exists()
    ).scalar()

    if nama_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama organisasi sudah digunakan",
        )

    new_organisasi = models.Organisasi(**organisasi_data.model_dump())
    db.add(new_organisasi)
    db.commit()
    db.refresh(new_organisasi)

    return new_organisasi


@router.put("/{organisasi_id}", response_model=schemas.OrganisasiResponse)
def update_organisasi(
    organisasi_id: int,
    organisasi_data: schemas.OrganisasiUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update organisasi (admin only)."""
    # Cek exist dulu dengan query ringan
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id
    ).first()

    if not organisasi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan",
        )

    updates = organisasi_data.model_dump(exclude_unset=True)
    if updates:
        # Jika nama diubah, cek duplikat terlebih dahulu
        if "nama" in updates and updates["nama"] != organisasi.nama:
            nama_exists = db.query(
                db.query(models.Organisasi).filter(models.Organisasi.nama == updates["nama"]).exists()
            ).scalar()
            if nama_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nama organisasi sudah digunakan",
                )

        # Bulk UPDATE — tidak ada setattr loop + refresh SELECT
        db.query(models.Organisasi).filter(
            models.Organisasi.id == organisasi_id
        ).update(updates, synchronize_session="fetch")
        db.commit()
        db.refresh(organisasi)

    return organisasi


@router.delete("/{organisasi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organisasi(
    organisasi_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete organisasi (admin only)."""
    # Langsung DELETE dan cek rowcount — satu query, tidak perlu SELECT dulu
    deleted = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id
    ).delete(synchronize_session=False)
    db.commit()

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan",
        )

    return None
