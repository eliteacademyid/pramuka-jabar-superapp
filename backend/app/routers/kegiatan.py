from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.limiter import limiter, LIMIT_READ_LIST, LIMIT_READ_DETAIL, LIMIT_WRITE, LIMIT_DELETE

router = APIRouter(prefix="/kegiatans", tags=["Kegiatans"])

_SORT_MAP = {
    "nama": models.Kegiatan.nama,
    "tanggal_mulai": models.Kegiatan.tanggal_mulai,
    "created_at": models.Kegiatan.created_at,
}


def _is_admin(user: models.User) -> bool:
    """Cek admin via nama role — tidak bergantung pada hardcoded role_id."""
    return user.role is not None and user.role.name == "admin"


@router.get("", response_model=List[schemas.KegiatanResponse])
@limiter.limit(LIMIT_READ_LIST)
def get_all_kegiatans(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    program_id: Optional[int] = Query(None, gt=0),
    status: Optional[str] = Query(None, max_length=20),
    search: Optional[str] = Query(None, max_length=100),
    sort_by: Optional[str] = Query("created_at"),
    order: Optional[str] = Query("desc"),
    db: Session = Depends(get_db),
):
    """Get all kegiatans. Limit: 60/menit per IP."""
    query = db.query(models.Kegiatan)

    if program_id:
        query = query.filter(models.Kegiatan.program_id == program_id)
    if status:
        query = query.filter(models.Kegiatan.status == status)
    if search:
        query = query.filter(models.Kegiatan.nama.ilike(f"%{search}%"))

    order_column = _SORT_MAP.get(sort_by, models.Kegiatan.created_at)
    if order.lower() == "asc":
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())

    return query.offset(skip).limit(limit).all()


@router.get("/{kegiatan_id}", response_model=schemas.KegiatanDetailResponse)
@limiter.limit(LIMIT_READ_DETAIL)
def get_kegiatan_by_id(request: Request, kegiatan_id: int, db: Session = Depends(get_db)):
    """Get kegiatan by ID. Limit: 120/menit per IP."""
    kegiatan = db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).first()
    if not kegiatan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kegiatan tidak ditemukan")
    return kegiatan


@router.post("", response_model=schemas.KegiatanResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_WRITE)
def create_kegiatan(
    request: Request,
    kegiatan_data: schemas.KegiatanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new kegiatan. Limit: 30/menit per IP."""
    program_exists = db.query(
        db.query(models.Program).filter(models.Program.id == kegiatan_data.program_id).exists()
    ).scalar()

    if not program_exists:
        raise HTTPException(status_code=400, detail="Program tidak ditemukan")

    if kegiatan_data.tanggal_selesai and kegiatan_data.tanggal_mulai > kegiatan_data.tanggal_selesai:
        raise HTTPException(status_code=400, detail="Tanggal selesai harus lebih besar dari tanggal mulai")

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
@limiter.limit(LIMIT_WRITE)
def update_kegiatan(
    request: Request,
    kegiatan_id: int,
    kegiatan_data: schemas.KegiatanUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update kegiatan. Limit: 30/menit per IP."""
    kegiatan = (
        db.query(models.Kegiatan)
        .options(joinedload(models.Kegiatan.program))
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )
    if not kegiatan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kegiatan tidak ditemukan")

    # Guard null program — cegah AttributeError
    program_creator = kegiatan.program.creator_id if kegiatan.program else None
    if program_creator != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki izin untuk mengubah kegiatan ini")

    updates = kegiatan_data.model_dump(exclude_unset=True)
    if updates:
        db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).update(
            updates, synchronize_session="fetch"
        )
        db.commit()
        db.refresh(kegiatan)

    return kegiatan


@router.delete("/{kegiatan_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(LIMIT_DELETE)
def delete_kegiatan(
    request: Request,
    kegiatan_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete kegiatan. Limit: 20/menit per IP."""
    kegiatan = (
        db.query(models.Kegiatan)
        .options(joinedload(models.Kegiatan.program))
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )
    if not kegiatan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kegiatan tidak ditemukan")

    program_creator = kegiatan.program.creator_id if kegiatan.program else None
    if program_creator != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki izin untuk menghapus kegiatan ini")

    db.delete(kegiatan)
    db.commit()
    return None
