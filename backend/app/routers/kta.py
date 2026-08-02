from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/kta", tags=["kta"])


def _anggota_detail(db: Session, anggota_id: int) -> schemas.KtaDetailOut:
    anggota = db.query(models.Anggota).filter(models.Anggota.id == anggota_id).first()
    if not anggota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anggota tidak ditemukan"
        )
    return anggota


def _kta_or_404(db: Session, kta_id: int) -> models.Kta:
    kta = db.query(models.Kta).filter(models.Kta.id == kta_id).first()
    if not kta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="KTA tidak ditemukan"
        )
    return kta


def _generate_nomor_kta(db: Session, anggota: models.Anggota) -> str:
    year = datetime.utcnow().year
    count = db.query(models.Kta).count() + 1
    return f"KTA/{year}/{count:05d}"


def _build_detail(kta: models.Kta, db: Session) -> dict:
    anggota = db.query(models.Anggota).filter(models.Anggota.id == kta.anggota_id).first()
    gudep = db.query(models.Gudep).filter(models.Gudep.id == anggota.gudep_id).first() if anggota else None
    wilayah = db.query(models.Wilayah).filter(models.Wilayah.id == gudep.wilayah_id).first() if gudep else None
    kwarran = wilayah.nama if wilayah and wilayah.tingkat == "Kwartir Ranting" else None
    kwarcab = None
    if wilayah:
        if wilayah.tingkat == "Kwartir Cabang":
            kwarcab = wilayah.nama
        elif wilayah.parent_id:
            cabang = db.query(models.Wilayah).filter(models.Wilayah.id == wilayah.parent_id).first()
            kwarcab = cabang.nama if cabang else None
    return {
        "id": kta.id,
        "anggota_id": kta.anggota_id,
        "nomor_kta": kta.nomor_kta,
        "tanggal_terbit": kta.tanggal_terbit,
        "tanggal_berlaku": kta.tanggal_berlaku,
        "qr_data": kta.qr_data,
        "status": kta.status,
        "nta": anggota.nta if anggota else None,
        "nama_lengkap": anggota.nama_lengkap if anggota else None,
        "jenjang": anggota.jenjang if anggota else None,
        "jenis_kelamin": anggota.jenis_kelamin if anggota else None,
        "alamat": anggota.alamat if anggota else None,
        "gudep": gudep.nama if gudep else None,
        "kwarran": kwarran,
        "kwarcab": kwarcab,
    }


@router.get("/", response_model=List[schemas.KtaDetailOut])
def list_kta(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    ktas = db.query(models.Kta).order_by(models.Kta.id.desc()).all()
    return [_build_detail(k, db) for k in ktas]


@router.post("/generate/{anggota_id}", response_model=schemas.KtaDetailOut)
def generate_kta(
    anggota_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    anggota = _anggota_detail(db, anggota_id)
    existing = db.query(models.Kta).filter(models.Kta.anggota_id == anggota_id).first()
    if existing:
        return _build_detail(existing, db)

    nomor_kta = _generate_nomor_kta(db, anggota)
    qr_data = (
        f"KTA {nomor_kta} | NTA {anggota.nta} | {anggota.nama_lengkap} | "
        f"{anggota.jenjang} | {anggota.gudep_id}"
    )
    kta = models.Kta(
        anggota_id=anggota_id,
        nomor_kta=nomor_kta,
        tanggal_terbit=datetime.utcnow(),
        tanggal_berlaku=datetime.utcnow() + timedelta(days=365 * 3),
        qr_data=qr_data,
        status="aktif",
    )
    db.add(kta)
    db.commit()
    db.refresh(kta)
    return _build_detail(kta, db)


@router.get("/{kta_id}", response_model=schemas.KtaDetailOut)
def get_kta(
    kta_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    kta = _kta_or_404(db, kta_id)
    return _build_detail(kta, db)
