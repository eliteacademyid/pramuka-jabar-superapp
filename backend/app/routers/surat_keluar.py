from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/surat-keluar", tags=["surat-keluar"])

# Angka Romawi
ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
    6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X",
    11: "XI", 12: "XII",
}


def _generate_nomor_surat(db: Session) -> str:
    """Generate nomor surat otomatis: {seq}/KWARDA-JABAR/{bulan_romawi}/{tahun}"""
    now = datetime.utcnow()
    tahun = now.year
    bulan_romawi = ROMAN[now.month]

    # Hitung jumlah surat keluar tahun ini
    count = (
        db.query(func.count(models.Surat.id))
        .filter(
            models.Surat.jenis == "keluar",
            extract("year", models.Surat.created_at) == tahun,
            models.Surat.nomor_surat.isnot(None),
        )
        .scalar()
    ) or 0

    seq = count + 1
    nomor = f"{seq:03d}/KWARDA-JABAR/{bulan_romawi}/{tahun}"

    # Pastikan nomor unik
    while db.query(models.Surat).filter(models.Surat.nomor_surat == nomor).first():
        seq += 1
        nomor = f"{seq:03d}/KWARDA-JABAR/{bulan_romawi}/{tahun}"

    return nomor


def _record_audit(db: Session, surat_id: int, user_id: int, aktivitas: str, keterangan: str = None):
    log = models.AuditLog(
        surat_id=surat_id,
        user_id=user_id,
        aktivitas=aktivitas,
        keterangan=keterangan,
    )
    db.add(log)


def _enrich_surat(db: Session, surat: models.Surat) -> dict:
    data = surat.__dict__.copy()
    creator = db.query(models.User).filter(models.User.id == surat.created_by).first()
    data["created_by_info"] = creator
    data["lampiran"] = db.query(models.Lampiran).filter(models.Lampiran.surat_id == surat.id).all()
    disposisi_list = db.query(models.Disposisi).filter(models.Disposisi.surat_id == surat.id).all()
    enriched = []
    for d in disposisi_list:
        d_data = d.__dict__.copy()
        d_data["dari_user_info"] = db.query(models.User).filter(models.User.id == d.dari_user).first()
        d_data["kepada_user_info"] = db.query(models.User).filter(models.User.id == d.kepada_user).first()
        enriched.append(d_data)
    data["disposisi"] = enriched
    return data


@router.get("", response_model=List[schemas.SuratListOut])
def list_surat_keluar(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Surat).filter(models.Surat.jenis == "keluar")
    if status:
        q = q.filter(models.Surat.status == status)
    if search:
        q = q.filter(
            (models.Surat.perihal.ilike(f"%{search}%")) |
            (models.Surat.tujuan.ilike(f"%{search}%")) |
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
def get_surat_keluar(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "keluar"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat keluar tidak ditemukan")
    return _enrich_surat(db, surat)


@router.post("", response_model=schemas.SuratOut, status_code=status.HTTP_201_CREATED)
def create_surat_keluar(
    payload: schemas.SuratCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = models.Surat(
        jenis="keluar",
        pengirim=payload.pengirim,
        tujuan=payload.tujuan,
        tanggal_surat=payload.tanggal_surat,
        perihal=payload.perihal,
        isi=payload.isi,
        status="Draft",
        created_by=current_user.id,
    )
    db.add(surat)
    db.commit()
    db.refresh(surat)

    _record_audit(db, surat.id, current_user.id, "Surat Keluar Dibuat (Draft)",
                  f"Perihal: {surat.perihal}")
    db.commit()
    return _enrich_surat(db, surat)


@router.put("/{surat_id}", response_model=schemas.SuratOut)
def update_surat_keluar(
    surat_id: int,
    payload: schemas.SuratUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "keluar"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat keluar tidak ditemukan")

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
    _record_audit(db, surat.id, current_user.id, "Surat Keluar Diperbarui", keterangan)
    db.commit()
    return _enrich_surat(db, surat)


@router.post("/{surat_id}/approve", response_model=schemas.SuratOut)
def approve_surat_keluar(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Generate nomor surat otomatis dan ubah status ke Diverifikasi."""
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "keluar"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat keluar tidak ditemukan")
    if surat.status != "Draft":
        raise HTTPException(status_code=400, detail="Hanya surat berstatus Draft yang bisa di-approve")

    surat.nomor_surat = _generate_nomor_surat(db)
    surat.status = "Diverifikasi"
    surat.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(surat)

    _record_audit(db, surat.id, current_user.id, "Surat Keluar Diverifikasi",
                  f"Nomor surat: {surat.nomor_surat}")
    db.commit()
    return _enrich_surat(db, surat)


@router.delete("/{surat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_surat_keluar(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(
        models.Surat.id == surat_id,
        models.Surat.jenis == "keluar"
    ).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat keluar tidak ditemukan")
    db.delete(surat)
    db.commit()
