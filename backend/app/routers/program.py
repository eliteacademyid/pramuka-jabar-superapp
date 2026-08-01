from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/programs", tags=["Programs"])

# Peta kolom sort — dideklarasikan sekali, tidak dievaluasi ulang tiap request
_SORT_MAP = {
    "nama": models.Program.nama,
    "tahun": models.Program.tahun,
    "created_at": models.Program.created_at,
}


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
    """Get all programs with filtering, search, and pagination."""
    query = db.query(models.Program)

    if search:
        query = query.filter(models.Program.nama.ilike(f"%{search}%"))
    if tahun:
        query = query.filter(models.Program.tahun == tahun)
    if status:
        query = query.filter(models.Program.status == status)

    order_column = _SORT_MAP.get(sort_by, models.Program.created_at)
    query = query.order_by(
        order_column.asc() if order.lower() == "asc" else order_column.desc()
    )

    # Hapus query.count() — tidak dikembalikan ke client, hanya buang 1 round-trip
    return query.offset(skip).limit(limit).all()


@router.get("/{program_id}", response_model=schemas.ProgramDetailResponse)
def get_program_by_id(program_id: int, db: Session = Depends(get_db)):
    """Get program by ID."""
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
    """Create new program."""
    if not program_data.nama or not program_data.nama.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama program tidak boleh kosong",
        )

    if not (1900 <= program_data.tahun <= 2100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tahun tidak valid",
        )

    # EXISTS — tidak fetch semua kolom organisasi
    organisasi_exists = db.query(
        db.query(models.Organisasi)
        .filter(models.Organisasi.id == program_data.organisasi_id)
        .exists()
    ).scalar()

    if not organisasi_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organisasi tidak ditemukan",
        )

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
    """Update program."""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()

    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program tidak ditemukan",
        )

    if program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk mengubah program ini",
        )

    # Kumpulkan field yang berubah saja, lalu satu UPDATE query
    updates = program_data.model_dump(exclude_unset=True)
    if updates:
        db.query(models.Program).filter(models.Program.id == program_id).update(
            updates, synchronize_session="fetch"
        )
        db.commit()
        # Terapkan update ke object yang sudah ada di memory — tidak perlu SELECT ulang
        for k, v in updates.items():
            setattr(program, k, v)

    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete program."""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()

    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program tidak ditemukan",
        )

    if program.creator_id != current_user.id and current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki izin untuk menghapus program ini",
        )

    # Langsung DELETE — tidak perlu SELECT lagi, object sudah ada di session
    db.delete(program)
    db.commit()

    return None
