from datetime import date, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app import models
from app.database import get_db
from app.hub_utils import nama_wilayah

router = APIRouter(prefix="/public", tags=["beranda"])


def _statistik_keanggotaan(db: Session) -> dict:
    golongan = {"siaga": 0, "penggalang": 0, "penegak": 0, "pandega": 0, "dewasa": 0}
    rows = (
        db.query(models.Anggota.golongan, func.count(models.Anggota.id))
        .group_by(models.Anggota.golongan)
        .all()
    )
    for gol, jumlah in rows:
        key = gol if gol in golongan else "dewasa"
        golongan[key] = jumlah
    return {
        "total_siaga": golongan["siaga"],
        "total_penggalang": golongan["penggalang"],
        "total_penegak": golongan["penegak"],
        "total_pandega": golongan["pandega"],
        "total_dewasa": golongan["dewasa"],
        "total_kwarcab": db.query(models.Kwarcab).count(),
        "total_kwaran": db.query(models.Kwaran).count(),
        "total_gudep": db.query(models.Gudep).count(),
    }


def _berita_terbaru(db: Session) -> list:
    rows = (
        db.query(models.HubKegiatan)
        .options(joinedload(models.HubKegiatan.media))
        .filter(models.HubKegiatan.status == "approved")
        .order_by(
            models.HubKegiatan.tanggal_kegiatan.desc(),
            models.HubKegiatan.id.desc(),
        )
        .limit(5)
        .all()
    )
    result = []
    for h in rows:
        foto = next(
            (m.file_url for m in h.media if m.tipe == "foto"), None
        )
        result.append(
            {
                "id": h.id,
                "judul": h.judul,
                "ringkasan": h.deskripsi,
                "gambar": foto,
                "tanggal_kegiatan": h.tanggal_kegiatan,
                "tingkat_wilayah": h.tingkat_wilayah,
                "nama_wilayah": nama_wilayah(db, h.tingkat_wilayah, h.wilayah_id),
                "kategori": h.kategori,
            }
        )
    return result


def _agenda_mendatang(db: Session) -> list:
    today = date.today()
    rows = (
        db.query(models.Kegiatan)
        .filter(
            models.Kegiatan.untuk_publik.is_(True),
            models.Kegiatan.status.in_(["rencana", "berjalan"]),
            models.Kegiatan.tanggal_mulai >= today,
        )
        .order_by(models.Kegiatan.tanggal_mulai.asc())
        .limit(5)
        .all()
    )
    return [
        {
            "id": k.id,
            "judul": k.judul,
            "tanggal_mulai": k.tanggal_mulai,
            "lokasi": k.lokasi,
        }
        for k in rows
    ]


def _produk_unggulan(db: Session) -> list:
    rows = (
        db.query(models.Produk)
        .options(joinedload(models.Produk.toko))
        .join(models.Toko, models.Toko.id == models.Produk.toko_id)
        .filter(models.Produk.status == "aktif", models.Toko.status == "aktif")
        .order_by(models.Produk.id.desc())
        .limit(6)
        .all()
    )
    return [
        {
            "id": p.id,
            "foto_url": p.foto_url,
            "nama_produk": p.nama_produk,
            "harga": p.harga,
            "nama_toko": p.toko.nama_toko if p.toko else "",
        }
        for p in rows
    ]


def _transparansi_ringkas(db: Session) -> dict:
    tahun = date.today().year
    total_anggaran = (
        db.query(func.coalesce(func.sum(models.AnggaranProgram.jumlah_anggaran), 0))
        .filter(models.AnggaranProgram.tahun_anggaran == tahun)
        .scalar()
    )
    total_realisasi = (
        db.query(func.coalesce(func.sum(models.RealisasiAnggaran.jumlah_realisasi), 0))
        .join(
            models.AnggaranProgram,
            models.AnggaranProgram.id
            == models.RealisasiAnggaran.anggaran_program_id,
        )
        .filter(
            models.RealisasiAnggaran.status == "disetujui",
            models.AnggaranProgram.tahun_anggaran == tahun,
        )
        .scalar()
    )
    persen = None
    if total_anggaran and total_anggaran > 0:
        persen = round((total_realisasi / total_anggaran) * 100, 1)
    return {
        "tahun": tahun,
        "total_anggaran": total_anggaran,
        "total_realisasi": total_realisasi,
        "persen_penyerapan": persen,
    }


@router.get("/beranda")
def get_beranda(db: Session = Depends(get_db)):
    return {
        "statistik_keanggotaan": _statistik_keanggotaan(db),
        "berita_terbaru": _berita_terbaru(db),
        "agenda_mendatang": _agenda_mendatang(db),
        "produk_unggulan": _produk_unggulan(db),
        "transparansi_ringkas": _transparansi_ringkas(db),
        "diambil_pada": datetime.utcnow(),
    }
