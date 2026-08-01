from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/kegiatans", tags=["Kegiatans"])


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
    
    # Filter by program (Task 6.10)
    if program_id:
        query = query.filter(models.Kegiatan.program_id == program_id)
    
    # Filter by status (Task 6.11)
    if status:
        query = query.filter(models.Kegiatan.status == status)
    
    # Search by nama (Task 6.13)
    if search:
        query = query.filter(models.Kegiatan.nama.ilike(f"%{search}%"))
    
    # Sorting
    if sort_by == "created_at":
        order_column = models.Kegiatan.created_at
    elif sort_by == "nama":
        order_column = models.Kegiatan.nama
    elif sort_by == "tanggal_mulai":
        order_column = models.Kegiatan.tanggal_mulai
    else:
        order_column = models.Kegiatan.created_at
    
    if order.lower() == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
    
    # Pagination (Task 6.14)
    total = query.count()
    kegiatans = query.offset(skip).limit(limit).all()
    
    return kegiatans


@router.get("/{kegiatan_id}", response_model=schemas.KegiatanDetailResponse)
def get_kegiatan_by_id(kegiatan_id: int, db: Session = Depends(get_db)):
    """Get kegiatan by ID (Task 6.5)"""
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
    """Create new kegiatan (Task 6.6)"""
    # Validate input (Task 6.7)
    if not kegiatan_data.nama or len(kegiatan_data.nama.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama kegiatan tidak boleh kosong",
        )
    
    # Check if program exists
    program = db.query(models.Program).filter(
        models.Program.id == kegiatan_data.program_id
    ).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program tidak ditemukan",
        )
    
    # Validate dates
    if kegiatan_data.tanggal_selesai and kegiatan_data.tanggal_mulai > kegiatan_data.tanggal_selesai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tanggal selesai harus lebih besar dari tanggal mulai",
        )
    
    # Create new kegiatan
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
    """Update kegiatan (Task 6.8)"""
    kegiatan = db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).first()
    
    if not kegiatan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kegiatan tidak ditemukan",
        )
    
    # Check permission through program creator or admin
    program = db.query(models.Program).filter(models.Program.id == kegiatan.program_id).first()
    if program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk mengubah kegiatan ini",
        )
    
    # Update fields
    if kegiatan_data.nama is not None:
        kegiatan.nama = kegiatan_data.nama
    if kegiatan_data.deskripsi is not None:
        kegiatan.deskripsi = kegiatan_data.deskripsi
    if kegiatan_data.tanggal_mulai is not None:
        kegiatan.tanggal_mulai = kegiatan_data.tanggal_mulai
    if kegiatan_data.tanggal_selesai is not None:
        kegiatan.tanggal_selesai = kegiatan_data.tanggal_selesai
    if kegiatan_data.status is not None:
        kegiatan.status = kegiatan_data.status
    if kegiatan_data.lokasi is not None:
        kegiatan.lokasi = kegiatan_data.lokasi
    
    db.commit()
    db.refresh(kegiatan)
    
    return kegiatan


@router.delete("/{kegiatan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kegiatan(
    kegiatan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete kegiatan (Task 6.9)"""
    kegiatan = db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).first()
    
    if not kegiatan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kegiatan tidak ditemukan",
        )
    
    # Check permission through program creator or admin
    program = db.query(models.Program).filter(models.Program.id == kegiatan.program_id).first()
    if program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk menghapus kegiatan ini",
        )
    
    db.delete(kegiatan)
    db.commit()
    
    return None
