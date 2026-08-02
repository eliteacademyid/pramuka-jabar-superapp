from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/rekap", tags=["rekap"])


@router.get("/anggota/jenjang")
def rekap_per_jenjang(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Anggota.jenjang, func.count(models.Anggota.id))
        .group_by(models.Anggota.jenjang)
        .order_by(models.Anggota.jenjang)
        .all()
    )
    return [{"jenjang": jenjang, "jumlah": count} for jenjang, count in rows]


@router.get("/anggota/wilayah")
def rekap_per_wilayah(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Wilayah.nama, func.count(models.Anggota.id))
        .join(models.Gudep, models.Gudep.wilayah_id == models.Wilayah.id)
        .join(models.Anggota, models.Anggota.gudep_id == models.Gudep.id)
        .group_by(models.Wilayah.nama)
        .order_by(func.count(models.Anggota.id).desc())
        .all()
    )
    return [{"wilayah": nama, "jumlah": count} for nama, count in rows]


@router.get("/kompetensi/jenjang")
def rekap_kompetensi_per_jenjang(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.KompetensiMaster.jenjang, func.count(models.KompetensiMaster.id))
        .group_by(models.KompetensiMaster.jenjang)
        .order_by(models.KompetensiMaster.jenjang)
        .all()
    )
    return [{"jenjang": jenjang, "jumlah": count} for jenjang, count in rows]


@router.get("/capaian/jenjang")
def rekap_capaian_per_jenjang(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Anggota.jenjang, func.count(models.CapaianKompetensi.id))
        .join(models.CapaianKompetensi, models.CapaianKompetensi.anggota_id == models.Anggota.id)
        .group_by(models.Anggota.jenjang)
        .order_by(models.Anggota.jenjang)
        .all()
    )
    return [{"jenjang": jenjang, "jumlah": count} for jenjang, count in rows]
