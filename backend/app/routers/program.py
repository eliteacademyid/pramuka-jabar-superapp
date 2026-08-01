from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/programs", tags=["Programs"])


@router.get("", response_model=List[schemas.ProgramResponse])
def get_all_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    tahun: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
):
    """Get all programs with filtering, search, and pagination"""
    query = db.query(models.Program)
    
    # Search by nama (Task 5.11)
    if search:
        query = query.filter(models.Program.nama.ilike(f"%{search}%"))
    
    # Filter by tahun (Task 5.12)
    if tahun:
        query = query.filter(models.Program.tahun == tahun)
    
    # Filter by status (Task 5.13)
    if status:
        query = query.filter(models.Program.status == status)
    
    # Sorting (Task 5.15)
    if sort_by == "created_at":
        order_column = models.Program.created_at
    elif sort_by == "nama":
        order_column = models.Program.nama
    elif sort_by == "tahun":
        order_column = models.Program.tahun
    else:
        order_column = models.Program.created_at
    
    if order.lower() == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
    
    # Pagination (Task 5.14)
    total = query.count()
    programs = query.offset(skip).limit(limit).all()
    
    return programs


@router.get("/{program_id}", response_model=schemas.ProgramDetailResponse)
def get_program_by_id(program_id: int, db: Session = Depends(get_db)):
    """Get program by ID (Task 5.6)"""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program tidak ditemukan",
        )
    
    return program


@router.post("", response_model=schemas.ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program_data: schemas.ProgramCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new program (Task 5.7)"""
    # Validate input (Task 5.8)
    if not program_data.nama or len(program_data.nama.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama program tidak boleh kosong",
        )
    
    if program_data.tahun < 1900 or program_data.tahun > 2100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tahun tidak valid",
        )
    
    # Check if organisasi exists
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == program_data.organisasi_id
    ).first()
    
    if not organisasi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organisasi tidak ditemukan",
        )
    
    # Create new program
    new_program = models.Program(
        nama=program_data.nama,
        deskripsi=program_data.deskripsi,
        tahun=program_data.tahun,
        status=program_data.status,
        creator_id=current_user.id,
        organisasi_id=program_data.organisasi_id,
    )
    
    db.add(new_program)
    db.commit()
    db.refresh(new_program)
    
    return new_program


@router.put("/{program_id}", response_model=schemas.ProgramResponse)
def update_program(
    program_id: int,
    program_data: schemas.ProgramUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update program (Task 5.9)"""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program tidak ditemukan",
        )
    
    # Check if user is creator or admin
    if program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk mengubah program ini",
        )
    
    # Update fields
    if program_data.nama is not None:
        program.nama = program_data.nama
    if program_data.deskripsi is not None:
        program.deskripsi = program_data.deskripsi
    if program_data.tahun is not None:
        program.tahun = program_data.tahun
    if program_data.status is not None:
        program.status = program_data.status
    
    db.commit()
    db.refresh(program)
    
    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete program (Task 5.10)"""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program tidak ditemukan",
        )
    
    # Check if user is creator or admin
    if program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk menghapus program ini",
        )
    
    db.delete(program)
    db.commit()
    
    return None
