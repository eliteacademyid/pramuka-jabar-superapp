import uuid
from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import UPLOAD_DIR
from app.database import get_db
from app.deps import get_current_kontributor
from app.hub_utils import serialize_hub

router = APIRouter(prefix="/kontributor", tags=["kontributor"])


def _get_milik_or_404(db: Session, user, hub_id: int) -> models.HubKegiatan:
    hub = (
        db.query(models.HubKegiatan)
        .filter(
            models.HubKegiatan.id == hub_id,
            models.HubKegiatan.submitted_by == user.id,
        )
        .first()
    )
    if not hub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postingan tidak ditemukan",
        )
    return hub


@router.post(
    "/hub-kegiatan",
    response_model=schemas.HubKegiatanOut,
    status_code=status.HTTP_201_CREATED,
)
def submit_hub_kegiatan(
    payload: schemas.HubKegiatanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_kontributor),
):
    if payload.kategori not in models.HUB_KATEGORI:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Kategori tidak valid"
        )
    hub = models.HubKegiatan(
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        kategori=payload.kategori,
        tingkat_wilayah=current_user.tingkat_wilayah,
        wilayah_id=current_user.wilayah_id,
        tanggal_kegiatan=payload.tanggal_kegiatan,
        lokasi=payload.lokasi,
        status="pending",
        submitted_by=current_user.id,
    )
    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


@router.get("/hub-kegiatan/saya")
def list_hub_kegiatan_saya(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_kontributor),
):
    rows = (
        db.query(models.HubKegiatan)
        .filter(models.HubKegiatan.submitted_by == current_user.id)
        .order_by(models.HubKegiatan.id.desc())
        .all()
    )
    return [serialize_hub(db, h) for h in rows]


@router.put("/hub-kegiatan/{hub_id}", response_model=schemas.HubKegiatanOut)
def update_hub_kegiatan(
    hub_id: int,
    payload: schemas.HubKegiatanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_kontributor),
):
    hub = _get_milik_or_404(db, current_user, hub_id)
    if hub.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Postingan sudah direview, tidak bisa diedit lagi",
        )
    data = payload.model_dump(exclude_unset=True)
    if data.get("kategori") and data["kategori"] not in models.HUB_KATEGORI:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Kategori tidak valid"
        )
    for field, value in data.items():
        setattr(hub, field, value)
    db.commit()
    db.refresh(hub)
    return hub


@router.post(
    "/hub-kegiatan/{hub_id}/media",
    response_model=schemas.HubKegiatanMediaOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_media_hub(
    hub_id: int,
    tipe: str = Query(default="foto"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_kontributor),
):
    hub = _get_milik_or_404(db, current_user, hub_id)
    if hub.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Postingan sudah direview, tidak bisa tambah media",
        )
    if tipe not in models.HUB_MEDIA_TIPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tipe media tidak valid"
        )

    ext = Path(file.filename or "").suffix.lower()
    if ext not in models.MEDIA_EXT_IZIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipe file tidak diizinkan (foto: jpg/png; video: mp4/webm/mov)",
        )

    ukuran = 0
    potongan = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        ukuran += len(chunk)
        potongan.append(chunk)
        if ukuran > models.MEDIA_MAX_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ukuran file melebihi {models.MEDIA_MAX_MB} MB",
            )

    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    nama_tersimpan = f"{uuid.uuid4().hex}{ext}"
    tujuan = Path(UPLOAD_DIR) / nama_tersimpan
    with open(tujuan, "wb") as out:
        for chunk in potongan:
            out.write(chunk)

    urutan_terakhir = (
        db.query(models.HubKegiatanMedia)
        .filter(models.HubKegiatanMedia.hub_kegiatan_id == hub_id)
        .count()
    )
    media = models.HubKegiatanMedia(
        hub_kegiatan_id=hub_id,
        tipe=tipe,
        file_url=f"/uploads/{nama_tersimpan}",
        urutan=urutan_terakhir,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media
