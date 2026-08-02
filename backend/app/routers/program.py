from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.limiter import limiter, LIMIT_READ_LIST, LIMIT_READ_DETAIL, LIMIT_WRITE, LIMIT_DELETE

router = APIRouter(prefix="/programs", tags=["Programs"])

_SORT_MAP = {
    "nama": models.Program.nama,
    "tahun": models.Program.tahun,
    "created_at": models.Program.created_at,
}


def _is_admin(user: models.User) -> bool:
    """Cek admin via nama role — tidak bergantung pada hardcoded role_id."""
    return user.role is not None and user.role.name == "admin"


@router.get("", response_model=List[schemas.ProgramResponse])
@limiter.limit(LIMIT_READ_LIST)
def get_all_programs(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    tahun: Optional[int] = Query(None, ge=1900, le=2100),
    status: Optional[str] = Query(None, max_length=20),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
):
    """Get all programs. Limit: 60/menit per IP."""
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
    return query.offset(skip).limit(limit).all()


@router.get("/{program_id}", response_model=schemas.ProgramDetailResponse)
@limiter.limit(LIMIT_READ_DETAIL)
def get_program_by_id(request: Request, program_id: int, db: Session = Depends(get_db)):
    """Get program by ID. Limit: 120/menit per IP."""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program tidak ditemukan")
    return program


@router.post("", response_model=schemas.ProgramResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_WRITE)
def create_program(
    request: Request,
    program_data: schemas.ProgramCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new program. Limit: 30/menit per IP."""
    organisasi_exists = db.query(
        db.query(models.Organisasi)
        .filter(models.Organisasi.id == program_data.organisasi_id)
        .exists()
    ).scalar()

    if not organisasi_exists:
        raise HTTPException(status_code=400, detail="Organisasi tidak ditemukan")

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
@limiter.limit(LIMIT_WRITE)
def update_program(
    request: Request,
    program_id: int,
    program_data: schemas.ProgramUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update program. Limit: 30/menit per IP."""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program tidak ditemukan")

    if program.creator_id != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki izin untuk mengubah program ini")

    updates = program_data.model_dump(exclude_unset=True)
    if updates:
        db.query(models.Program).filter(models.Program.id == program_id).update(
            updates, synchronize_session="fetch"
        )
        db.commit()
        for k, v in updates.items():
            setattr(program, k, v)

    return program


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(LIMIT_DELETE)
def delete_program(
    request: Request,
    program_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete program. Limit: 20/menit per IP."""
    program = db.query(models.Program).filter(models.Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program tidak ditemukan")

    if program.creator_id != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki izin untuk menghapus program ini")

    db.delete(program)
    db.commit()
    return None
