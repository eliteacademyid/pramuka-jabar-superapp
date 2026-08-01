from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("", response_model=List[schemas.CertificateOut])
def list_certificates(
    certificate_type: Optional[str] = None,
    level: Optional[str] = None,
    issuing_authority: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(models.Certificate).filter(models.Certificate.is_active == True)
    if certificate_type:
        q = q.filter(models.Certificate.certificate_type == certificate_type)
    if level:
        q = q.filter(models.Certificate.level == level)
    if issuing_authority:
        q = q.filter(models.Certificate.issuing_authority == issuing_authority)
    return q.order_by(models.Certificate.level, models.Certificate.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()


@router.get("/{cert_id}", response_model=schemas.CertificateOut)
def get_certificate(cert_id: int, db: Session = Depends(get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat tidak ditemukan")
    return cert


@router.post("", response_model=schemas.CertificateOut, status_code=status.HTTP_201_CREATED)
def create_certificate(
    payload: schemas.CertificateCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(get_current_admin),
):
    existing = db.query(models.Certificate).filter(models.Certificate.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kode sertifikat sudah ada")
    cert = models.Certificate(**payload.model_dump(), created_by=admin.id)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.put("/{cert_id}", response_model=schemas.CertificateOut)
def update_certificate(
    cert_id: int,
    payload: schemas.CertificateUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat tidak ditemukan")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(cert, k, v)
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(
    cert_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    cert = db.query(models.Certificate).filter(models.Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat tidak ditemukan")
    db.delete(cert)
    db.commit()
