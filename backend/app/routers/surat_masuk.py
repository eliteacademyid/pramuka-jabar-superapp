from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/surat-masuk", tags=["surat-masuk"])


def _record_audit(db: Session, surat_id: int, user_id: int, aktivitas: str, keterangan: str = None):
    log = models.AuditLog(
        surat_id=surat_id,
        user_id=user_id,
        aktivitas=aktivitas,
        keterangan=keterangan,
    )
    db.add(log)


def _enrich_surat(db: Session, surat: models.Surat) -> dict:
    """Attach related objects into a dict for schema serialization."""
    data = surat.__dict__.copy()

    # created_by user info
    creator = db.query(models.User).filter(models.User.id == surat.created_by).first()
    data["created_by_info"] = creator

    # lampiran
    data["lampiran"] = db.query(models.Lampiran).filter(models.Lampiran.surat_id == surat.id).all()

    # disposisi
    disposisi_list = db.query(models.Disposisi).filter(models.Disposisi.surat_id == surat.id).all()
    enriched_disposisi = []
    for d in disposisi_list:
        d_data = d.__dict__.copy()
        d_data["dari_user_info"] = db.query(models.User).filter(models.User.id == d.dari_user).first()
        d_data["kepada_user_info"] = db.query(models.User).filter(models.User.id == d.kepada_user).first()
        enriched_disposisi.append(d_data)
    data["disposisi"] = enriched_disposisi

    return data


@router.get("", response_model=List[schemas.SuratListOut])
def list_surat_masuk(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Surat).filter(models.Surat.jenis == "masuk")

    if status:
        q = q.filter(models.Surat.status == status)
    if search:
        q = q.filter(
            (models.Surat.perihal.ilike(f"%{search}%")) |
            (models.Surat.pengirim.ilike(f"%{search}%")) |
            (models.Surat.nomor_surat.ilike(f"%{search}%"))
        )

    surats = q.order_by(models.Surat.created_at.desc()).all()

    result = []
    for s in surats:
        creator = db.query(models.User).filter(models.User.id == s.created_by).first()
        item = s.__dict__.copy()
        item["created_by_info"] = creator
        result.append(item)
    return result


@router.get("/{surat_id}", response_model=schemas.SuratOut)
def get_surat_masuk(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "masuk"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat masuk tidak ditemukan")
    return _enrich_surat(db, surat)


@router.post("", response_model=schemas.SuratOut, status_code=status.HTTP_201_CREATED)
def create_surat_masuk(
    payload: schemas.SuratCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = models.Surat(
        jenis="masuk",
        nomor_surat=payload.nomor_surat if hasattr(payload, "nomor_surat") else None,
        pengirim=payload.pengirim,
        tujuan=payload.tujuan,
        tanggal_surat=payload.tanggal_surat,
        tanggal_diterima=payload.tanggal_diterima,
        perihal=payload.perihal,
        isi=payload.isi,
        status=payload.status or "Draft",
        created_by=current_user.id,
    )
    db.add(surat)
    db.commit()
    db.refresh(surat)

    _record_audit(db, surat.id, current_user.id, "Surat Masuk Dibuat",
                  f"Perihal: {surat.perihal}")
    db.commit()

    return _enrich_surat(db, surat)


@router.put("/{surat_id}", response_model=schemas.SuratOut)
def update_surat_masuk(
    surat_id: int,
    payload: schemas.SuratUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "masuk"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat masuk tidak ditemukan")

    old_status = surat.status
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(surat, field, value)
    surat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(surat)

    keterangan = None
    if "status" in update_data and update_data["status"] != old_status:
        keterangan = f"Status berubah dari '{old_status}' menjadi '{surat.status}'"
    _record_audit(db, surat.id, current_user.id, "Surat Masuk Diperbarui", keterangan)
    db.commit()

    return _enrich_surat(db, surat)


@router.delete("/{surat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_surat_masuk(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "masuk"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat masuk tidak ditemukan")

    db.delete(surat)
    db.commit()
