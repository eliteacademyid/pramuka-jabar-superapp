from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app import models
from app.database import get_db
from app.hub_utils import serialize_hub_publik

router = APIRouter(prefix="/public", tags=["hub-publik"])


@router.get("/hub-kegiatan")
def list_hub_kegiatan_publik(
    kategori: Optional[str] = Query(default=None),
    tingkat_wilayah: Optional[str] = Query(default=None),
    wilayah_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=9, ge=1, le=48),
    db: Session = Depends(get_db),
):
    query = db.query(models.HubKegiatan).options(
        joinedload(models.HubKegiatan.media),
        joinedload(models.HubKegiatan.submitted_by_user),
        joinedload(models.HubKegiatan.reviewed_by_user),
    )
    query = query.filter(models.HubKegiatan.status == "approved")
    if kategori:
        query = query.filter(models.HubKegiatan.kategori == kategori)
    if tingkat_wilayah:
        query = query.filter(models.HubKegiatan.tingkat_wilayah == tingkat_wilayah)
    if wilayah_id:
        query = query.filter(models.HubKegiatan.wilayah_id == wilayah_id)

    total = query.count()
    rows = (
        query.order_by(
            models.HubKegiatan.tanggal_kegiatan.desc(),
            models.HubKegiatan.id.desc(),
        )
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [serialize_hub_publik(db, h) for h in rows],
    }


@router.get("/hub-kegiatan/{hub_id}")
def get_hub_kegiatan_publik(
    hub_id: int,
    db: Session = Depends(get_db),
):
    hub = (
        db.query(models.HubKegiatan)
        .options(
            joinedload(models.HubKegiatan.media),
            joinedload(models.HubKegiatan.submitted_by_user),
            joinedload(models.HubKegiatan.reviewed_by_user),
        )
        .filter(
            models.HubKegiatan.id == hub_id,
            models.HubKegiatan.status == "approved",
        )
        .first()
    )
    if not hub:
        raise HTTPException(status_code=404, detail="Postingan tidak ditemukan")
    return serialize_hub_publik(db, hub)
