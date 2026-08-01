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
    db: Session = Depends(get_db),
):
    """Get all organisasi"""
    organisasi_list = (
        db.query(models.Organisasi)
        .order_by(models.Organisasi.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return organisasi_list


@router.get("/{organisasi_id}", response_model=schemas.OrganisasiResponse)
def get_organisasi_by_id(organisasi_id: int, db: Session = Depends(get_db)):
    """Get organisasi by ID"""
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
    """Create new organisasi (admin only)"""
    # Check if nama already exists
    existing = db.query(models.Organisasi).filter(
        models.Organisasi.nama == organisasi_data.nama
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama organisasi sudah digunakan",
        )
    
    new_organisasi = models.Organisasi(**organisasi_data.dict())
    
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
    """Update organisasi (admin only)"""
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id
    ).first()
    
    if not organisasi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan",
        )
    
    # Update fields
    update_data = organisasi_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organisasi, field, value)
    
    db.commit()
    db.refresh(organisasi)
    
    return organisasi


@router.delete("/{organisasi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organisasi(
    organisasi_id: int,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Delete organisasi (admin only)"""
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id
    ).first()
    
    if not organisasi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan",
        )
    
    db.delete(organisasi)
    db.commit()
    
    return None
