from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin
from app.limiter import limiter, LIMIT_READ_LIST, LIMIT_READ_DETAIL, LIMIT_WRITE, LIMIT_DELETE

router = APIRouter(prefix="/organisasi", tags=["Organisasi"])


@router.get("", response_model=List[schemas.OrganisasiResponse])
@limiter.limit(LIMIT_READ_LIST)
def get_all_organisasi(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """List organisasi. Limit: 60/menit per IP."""
    query = db.query(models.Organisasi)
    if search:
        query = query.filter(models.Organisasi.nama.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.filter(models.Organisasi.is_active == is_active)
    return query.order_by(models.Organisasi.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{organisasi_id}", response_model=schemas.OrganisasiResponse)
@limiter.limit(LIMIT_READ_DETAIL)
def get_organisasi_by_id(request: Request, organisasi_id: int, db: Session = Depends(get_db)):
    """Detail organisasi. Limit: 120/menit per IP."""
    organisasi = db.query(models.Organisasi).filter(models.Organisasi.id == organisasi_id).first()
    if not organisasi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisasi tidak ditemukan")
    return organisasi


@router.post("", response_model=schemas.OrganisasiResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_WRITE)
def create_organisasi(
    request: Request,
    organisasi_data: schemas.OrganisasiCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Buat organisasi (admin). Limit: 30/menit per IP."""
    nama_exists = db.query(
        db.query(models.Organisasi).filter(models.Organisasi.nama == organisasi_data.nama).exists()
    ).scalar()
    if nama_exists:
        raise HTTPException(status_code=400, detail="Nama organisasi sudah digunakan")

    new_organisasi = models.Organisasi(**organisasi_data.model_dump())
    db.add(new_organisasi)
    db.commit()
    db.refresh(new_organisasi)
    return new_organisasi


@router.put("/{organisasi_id}", response_model=schemas.OrganisasiResponse)
@limiter.limit(LIMIT_WRITE)
def update_organisasi(
    request: Request,
    organisasi_id: int,
    organisasi_data: schemas.OrganisasiUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update organisasi (admin). Limit: 30/menit per IP."""
    organisasi = db.query(models.Organisasi).filter(models.Organisasi.id == organisasi_id).first()
    if not organisasi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisasi tidak ditemukan")

    updates = organisasi_data.model_dump(exclude_unset=True)
    if updates:
        if "nama" in updates and updates["nama"] != organisasi.nama:
            nama_exists = db.query(
                db.query(models.Organisasi).filter(models.Organisasi.nama == updates["nama"]).exists()
            ).scalar()
            if nama_exists:
                raise HTTPException(status_code=400, detail="Nama organisasi sudah digunakan")
        db.query(models.Organisasi).filter(models.Organisasi.id == organisasi_id).update(
            updates, synchronize_session="fetch"
        )
        db.commit()
        db.refresh(organisasi)
    return organisasi


@router.delete("/{organisasi_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(LIMIT_DELETE)
def delete_organisasi(
    request: Request,
    organisasi_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Hapus organisasi (admin). Limit: 20/menit per IP."""
    deleted = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id
    ).delete(synchronize_session=False)
    db.commit()
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisasi tidak ditemukan")
    return None
