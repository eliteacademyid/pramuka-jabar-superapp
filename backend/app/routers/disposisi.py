from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/disposisi", tags=["disposisi"])


def _record_audit(db: Session, surat_id: int, user_id: int, aktivitas: str, keterangan: str = None):
    log = models.AuditLog(
        surat_id=surat_id,
        user_id=user_id,
        aktivitas=aktivitas,
        keterangan=keterangan,
    )
    db.add(log)


def _enrich_disposisi(db: Session, d: models.Disposisi) -> dict:
    data = d.__dict__.copy()
    data["dari_user_info"] = db.query(models.User).filter(models.User.id == d.dari_user).first()
    data["kepada_user_info"] = db.query(models.User).filter(models.User.id == d.kepada_user).first()
    return data


@router.get("", response_model=List[schemas.DisposisiOut])
def list_disposisi(
    surat_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Disposisi)
    if surat_id:
        q = q.filter(models.Disposisi.surat_id == surat_id)
    disposisi_list = q.order_by(models.Disposisi.created_at.desc()).all()
    return [_enrich_disposisi(db, d) for d in disposisi_list]


@router.post("", response_model=schemas.DisposisiOut, status_code=status.HTTP_201_CREATED)
def create_disposisi(
    payload: schemas.DisposisiCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Validasi surat ada
    surat = db.query(models.Surat).filter(models.Surat.id == payload.surat_id).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat tidak ditemukan")

    # Validasi penerima ada
    penerima = db.query(models.User).filter(models.User.id == payload.kepada_user).first()
    if not penerima:
        raise HTTPException(status_code=404, detail="Pengguna penerima tidak ditemukan")

    disposisi = models.Disposisi(
        surat_id=payload.surat_id,
        dari_user=current_user.id,
        kepada_user=payload.kepada_user,
        catatan=payload.catatan,
        deadline=payload.deadline,
        status="Belum Dibaca",
    )
    db.add(disposisi)

    # Update status surat menjadi Didisposisi
    if surat.status not in ("Didisposisi", "Diproses", "Selesai", "Diarsipkan"):
        surat.status = "Didisposisi"
        surat.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(disposisi)

    _record_audit(db, payload.surat_id, current_user.id, "Disposisi Dibuat",
                  f"Kepada: {penerima.nama_lengkap}")
    db.commit()

    return _enrich_disposisi(db, disposisi)


@router.put("/{disposisi_id}", response_model=schemas.DisposisiOut)
def update_disposisi(
    disposisi_id: int,
    payload: schemas.DisposisiUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    disposisi = db.query(models.Disposisi).filter(models.Disposisi.id == disposisi_id).first()
    if not disposisi:
        raise HTTPException(status_code=404, detail="Disposisi tidak ditemukan")

    valid_statuses = models.STATUS_DISPOSISI
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status tidak valid. Pilihan: {', '.join(valid_statuses)}"
        )

    old_status = disposisi.status
    disposisi.status = payload.status
    if payload.catatan is not None:
        disposisi.catatan = payload.catatan
    disposisi.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(disposisi)

    _record_audit(db, disposisi.surat_id, current_user.id, "Status Disposisi Diperbarui",
                  f"'{old_status}' → '{disposisi.status}'")
    db.commit()

    return _enrich_disposisi(db, disposisi)
