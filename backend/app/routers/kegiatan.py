from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/kegiatans", tags=["Kegiatans"])

# Dideklarasikan di module level — tidak dibangun ulang tiap request
_SORT_MAP = {
    "nama": models.Kegiatan.nama,
    "tanggal_mulai": models.Kegiatan.tanggal_mulai,
    "created_at": models.Kegiatan.created_at,
}


@router.get("", response_model=List[schemas.KegiatanResponse])
def get_all_kegiatans(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    program_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
):
    """Get all kegiatans with filtering and pagination"""
    query = db.query(models.Kegiatan)

    if program_id:
        query = query.filter(models.Kegiatan.program_id == program_id)

    if status:
        query = query.filter(models.Kegiatan.status == status)

    if search:
        query = query.filter(models.Kegiatan.nama.ilike(f"%{search}%"))

    # Sorting
    order_column = _SORT_MAP.get(sort_by, models.Kegiatan.created_at)

    if order.lower() == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())

    # Satu query dengan LIMIT/OFFSET — tidak ada COUNT terpisah
    return query.offset(skip).limit(limit).all()


@router.get("/{kegiatan_id}", response_model=schemas.KegiatanDetailResponse)
def get_kegiatan_by_id(kegiatan_id: int, db: Session = Depends(get_db)):
    """Get kegiatan by ID"""
    kegiatan = db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).first()

    if not kegiatan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kegiatan tidak ditemukan",
        )

    return kegiatan


@router.post("", response_model=schemas.KegiatanResponse, status_code=status.HTTP_201_CREATED)
def create_kegiatan(
    kegiatan_data: schemas.KegiatanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new kegiatan"""
    if not kegiatan_data.nama or not kegiatan_data.nama.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama kegiatan tidak boleh kosong",
        )

    # Cek program dengan EXISTS — lebih efisien dari full SELECT *
    program_exists = db.query(
        db.query(models.Program).filter(models.Program.id == kegiatan_data.program_id).exists()
    ).scalar()

    if not program_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program tidak ditemukan",
        )

    if kegiatan_data.tanggal_selesai and kegiatan_data.tanggal_mulai > kegiatan_data.tanggal_selesai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tanggal selesai harus lebih besar dari tanggal mulai",
        )

    new_kegiatan = models.Kegiatan(
        nama=kegiatan_data.nama,
        deskripsi=kegiatan_data.deskripsi,
        program_id=kegiatan_data.program_id,
        tanggal_mulai=kegiatan_data.tanggal_mulai,
        tanggal_selesai=kegiatan_data.tanggal_selesai,
        status=kegiatan_data.status,
        lokasi=kegiatan_data.lokasi,
    )

    db.add(new_kegiatan)
    db.commit()
    db.refresh(new_kegiatan)

    return new_kegiatan


@router.put("/{kegiatan_id}", response_model=schemas.KegiatanResponse)
def update_kegiatan(
    kegiatan_id: int,
    kegiatan_data: schemas.KegiatanUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update kegiatan"""
    # Satu query: ambil kegiatan sekaligus dengan program-nya (joinedload)
    kegiatan = (
        db.query(models.Kegiatan)
        .options(joinedload(models.Kegiatan.program))
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )

    if not kegiatan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kegiatan tidak ditemukan",
        )

    # Cek permission — program sudah di-load dalam query di atas
    if kegiatan.program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk mengubah kegiatan ini",
        )

    # Kumpulkan field yang berubah, lalu UPDATE sekaligus
    updates = kegiatan_data.model_dump(exclude_unset=True)
    if updates:
        db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).update(
            updates, synchronize_session="fetch"
        )
        db.commit()
        # Refresh hanya jika perlu return data terbaru
        db.refresh(kegiatan)

    return kegiatan


@router.delete("/{kegiatan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kegiatan(
    kegiatan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete kegiatan"""
    # Satu query: ambil kegiatan sekaligus dengan program-nya (joinedload)
    kegiatan = (
        db.query(models.Kegiatan)
        .options(joinedload(models.Kegiatan.program))
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )

    if not kegiatan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kegiatan tidak ditemukan",
        )

    # Cek permission — program sudah di-load dalam query di atas
    if kegiatan.program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk menghapus kegiatan ini",
        )

    db.delete(kegiatan)
    db.commit()

    return None
