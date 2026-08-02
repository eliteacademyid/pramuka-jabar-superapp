from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin
from app.hub_utils import serialize_hub

router = APIRouter(prefix="/admin", tags=["hub-admin"])


def _get_hub_or_404(db: Session, hub_id: int) -> models.HubKegiatan:
    hub = (
        db.query(models.HubKegiatan)
        .options(
            joinedload(models.HubKegiatan.media),
            joinedload(models.HubKegiatan.submitted_by_user),
            joinedload(models.HubKegiatan.reviewed_by_user),
        )
        .filter(models.HubKegiatan.id == hub_id)
        .first()
    )
    if not hub:
        raise HTTPException(status_code=404, detail="Postingan tidak ditemukan")
    return hub


@router.get("/hub-kegiatan")
def list_hub_kegiatan(
    status_: Optional[str] = Query(default=None, alias="status"),
    tingkat_wilayah: Optional[str] = Query(default=None),
    kategori: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.HubKegiatan).options(
        joinedload(models.HubKegiatan.media),
        joinedload(models.HubKegiatan.submitted_by_user),
        joinedload(models.HubKegiatan.reviewed_by_user),
    )
    if status_:
        query = query.filter(models.HubKegiatan.status == status_)
    if tingkat_wilayah:
        query = query.filter(models.HubKegiatan.tingkat_wilayah == tingkat_wilayah)
    if kategori:
        query = query.filter(models.HubKegiatan.kategori == kategori)

    pending_first = models.HubKegiatan.status != "pending"
    rows = (
        query.order_by(
            pending_first, models.HubKegiatan.id.desc()
        ).all()
    )
    return [serialize_hub(db, h) for h in rows]


@router.patch("/hub-kegiatan/{hub_id}/approve")
def approve_hub_kegiatan(
    hub_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    hub = _get_hub_or_404(db, hub_id)
    if hub.status == "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Postingan sudah ditolak. Ubah dulu ke pending atau buat baru.",
        )
    hub.status = "approved"
    hub.catatan_moderasi = None
    hub.reviewed_by = current_admin.id
    db.commit()
    db.refresh(hub)
    return serialize_hub(db, hub)


@router.patch("/hub-kegiatan/{hub_id}/reject")
def reject_hub_kegiatan(
    hub_id: int,
    payload: schemas.HubKegiatanReject,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    if not payload.catatan_moderasi.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catatan moderasi wajib diisi sebagai alasan penolakan",
        )
    hub = _get_hub_or_404(db, hub_id)
    if hub.status == "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Postingan sudah disetujui",
        )
    hub.status = "rejected"
    hub.catatan_moderasi = payload.catatan_moderasi.strip()
    hub.reviewed_by = current_admin.id
    db.commit()
    db.refresh(hub)
    return serialize_hub(db, hub)


@router.get("/hub-kegiatan/rekap")
def rekap_hub_kegiatan(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    per_status = {}
    for s in models.HUB_STATUS:
        per_status[s] = (
            db.query(models.HubKegiatan)
            .filter(models.HubKegiatan.status == s)
            .count()
        )

    per_tingkat = {}
    for t in models.TINGKAT_WILAYAH:
        per_tingkat[t] = (
            db.query(models.HubKegiatan)
            .filter(models.HubKegiatan.tingkat_wilayah == t)
            .count()
        )

    rows = (
        db.query(
            models.HubKegiatan.tingkat_wilayah,
            models.HubKegiatan.wilayah_id,
            models.HubKegiatan.id,
        )
        .all()
    )
    wilayah_map = {}
    for tingkat, wilayah_id, _ in rows:
        key = f"{tingkat}:{wilayah_id}"
        entry = wilayah_map.setdefault(
            key,
            {"tingkat_wilayah": tingkat, "wilayah_id": wilayah_id, "jumlah": 0},
        )
        entry["jumlah"] += 1

    from app.hub_utils import nama_wilayah

    per_wilayah = []
    for entry in wilayah_map.values():
        entry["nama_wilayah"] = nama_wilayah(
            db, entry["tingkat_wilayah"], entry["wilayah_id"]
        )
        per_wilayah.append(entry)
    per_wilayah.sort(key=lambda x: x["jumlah"], reverse=True)

    total = db.query(models.HubKegiatan).count()
    return {
        "total": total,
        "per_status": per_status,
        "per_tingkat": per_tingkat,
        "per_wilayah": per_wilayah,
    }
