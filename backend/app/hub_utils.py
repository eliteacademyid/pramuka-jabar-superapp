from sqlalchemy.orm import Session

from app import models, schemas


def nama_wilayah(db: Session, tingkat: str, wilayah_id: int) -> str:
    if tingkat == "kwarcab":
        obj = db.query(models.Kwarcab).filter(models.Kwarcab.id == wilayah_id).first()
        return obj.nama if obj else ""
    if tingkat == "kwaran":
        obj = db.query(models.Kwaran).filter(models.Kwaran.id == wilayah_id).first()
        return obj.nama if obj else ""
    if tingkat == "gudep":
        obj = db.query(models.Gudep).filter(models.Gudep.id == wilayah_id).first()
        return obj.nama_pangkalan if obj else ""
    return ""


def serialize_hub(db: Session, hub: models.HubKegiatan) -> dict:
    data = schemas.HubKegiatanOut.model_validate(hub).model_dump()
    data["media"] = [
        schemas.HubKegiatanMediaOut.model_validate(m).model_dump() for m in hub.media
    ]
    data["nama_wilayah"] = nama_wilayah(db, hub.tingkat_wilayah, hub.wilayah_id)
    data["nama_submitter"] = (
        hub.submitted_by_user.nama_lengkap if hub.submitted_by_user else ""
    )
    data["nama_reviewer"] = (
        hub.reviewed_by_user.nama_lengkap if hub.reviewed_by_user else None
    )
    return data


def serialize_hub_publik(db: Session, hub: models.HubKegiatan) -> dict:
    """Serialisasi HANYA untuk endpoint publik.

    Tidak membocorkan identitas kontributor/petugas (nama user, email), catatan
    moderasi internal, maupun id user internal.
    """
    return {
        "id": hub.id,
        "judul": hub.judul,
        "deskripsi": hub.deskripsi,
        "kategori": hub.kategori,
        "tingkat_wilayah": hub.tingkat_wilayah,
        "wilayah_id": hub.wilayah_id,
        "nama_wilayah": nama_wilayah(db, hub.tingkat_wilayah, hub.wilayah_id),
        "tanggal_kegiatan": hub.tanggal_kegiatan,
        "lokasi": hub.lokasi,
        "created_at": hub.created_at,
        "media": [
            {
                "id": m.id,
                "tipe": m.tipe,
                "file_url": m.file_url,
                "urutan": m.urutan,
            }
            for m in hub.media
        ],
    }
