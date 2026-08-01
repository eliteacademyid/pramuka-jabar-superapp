from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["anggota"])


def _validate_anggota_payload(
    db: Session, payload, obj: Optional[models.Anggota] = None
):
    data = payload.model_dump(exclude_unset=True)

    if "golongan" in data and data["golongan"] not in models.GOLONGAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Golongan tidak valid"
        )

    golongan = data.get("golongan") or (obj.golongan if obj else None)

    if "jabatan_dewasa" in data:
        if golongan == "dewasa":
            if not data["jabatan_dewasa"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Jabatan wajib diisi untuk golongan Dewasa",
                )
            if data["jabatan_dewasa"] not in models.JABATAN_DEWASA:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Jabatan dewasa tidak valid",
                )
        else:
            data["jabatan_dewasa"] = None

    if "tanggal_lahir" in data and data["tanggal_lahir"]:
        if data["tanggal_lahir"] > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tanggal lahir tidak boleh di masa depan",
            )

    if "tanggal_bergabung" in data and data["tanggal_bergabung"]:
        if data["tanggal_bergabung"] > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tanggal bergabung tidak boleh di masa depan",
            )

    return data


def _check_nis_unik(db: Session, nis: str, exclude_id: Optional[int] = None):
    query = db.query(models.Anggota).filter(models.Anggota.nis_anggota == nis)
    if exclude_id is not None:
        query = query.filter(models.Anggota.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NIS anggota sudah digunakan",
        )


def _get_anggota_or_404(db: Session, anggota_id: int) -> models.Anggota:
    obj = db.query(models.Anggota).filter(models.Anggota.id == anggota_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anggota tidak ditemukan"
        )
    return obj


@router.get("/anggota")
def list_anggota(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    golongan: Optional[str] = Query(default=None),
    gudep_id: Optional[int] = Query(default=None),
    kwaran_id: Optional[int] = Query(default=None),
    kwarcab_id: Optional[int] = Query(default=None),
    status_aktif: Optional[bool] = Query(default=None),
    q: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = (
        db.query(models.Anggota)
        .join(models.Gudep, models.Anggota.gudep_id == models.Gudep.id)
        .join(models.Kwaran, models.Gudep.kwaran_id == models.Kwaran.id)
        .join(models.Kwarcab, models.Kwaran.kwarcab_id == models.Kwarcab.id)
    )

    if golongan:
        query = query.filter(models.Anggota.golongan == golongan)
    if gudep_id is not None:
        query = query.filter(models.Anggota.gudep_id == gudep_id)
    if kwaran_id is not None:
        query = query.filter(models.Gudep.kwaran_id == kwaran_id)
    if kwarcab_id is not None:
        query = query.filter(models.Kwaran.kwarcab_id == kwarcab_id)
    if status_aktif is not None:
        query = query.filter(models.Anggota.status_aktif == status_aktif)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Anggota.nama_lengkap.ilike(like)
            | models.Anggota.nis_anggota.ilike(like)
        )

    total = query.count()
    items = (
        query.order_by(models.Anggota.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    result = []
    for anggota in items:
        item = schemas.AnggotaOut.model_validate(anggota).model_dump()
        item["nama_gudep"] = anggota.gudep.nama_pangkalan
        item["nomor_gudep"] = anggota.gudep.nomor_gudep
        item["nama_kwaran"] = anggota.gudep.kwaran.nama
        item["nama_kwarcab"] = anggota.gudep.kwaran.kwarcab.nama
        result.append(item)

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": result,
    }


@router.post("/anggota", response_model=schemas.AnggotaOut, status_code=status.HTTP_201_CREATED)
def create_anggota(
    payload: schemas.AnggotaCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _check_nis_unik(db, payload.nis_anggota)
    if not db.query(models.Gudep).filter(models.Gudep.id == payload.gudep_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Gudep tidak ditemukan"
        )
    data = _validate_anggota_payload(db, payload)

    golongan = data.get("golongan", payload.golongan)
    if golongan == "dewasa":
        if not data.get("jabatan_dewasa"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jabatan wajib diisi untuk golongan Dewasa",
            )
    else:
        data["jabatan_dewasa"] = None

    obj = models.Anggota(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/anggota/{anggota_id}", response_model=schemas.AnggotaOut)
def update_anggota(
    anggota_id: int,
    payload: schemas.AnggotaUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_anggota_or_404(db, anggota_id)

    if payload.nis_anggota is not None and payload.nis_anggota != obj.nis_anggota:
        _check_nis_unik(db, payload.nis_anggota, exclude_id=anggota_id)

    if payload.gudep_id is not None and payload.gudep_id != obj.gudep_id:
        if not db.query(models.Gudep).filter(models.Gudep.id == payload.gudep_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Gudep tidak ditemukan"
            )

    data = _validate_anggota_payload(db, payload, obj=obj)

    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/anggota/{anggota_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anggota(
    anggota_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_anggota_or_404(db, anggota_id)
    obj.status_aktif = False
    db.commit()


@router.get("/anggota/statistik")
def statistik_anggota(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    aktif_query = db.query(models.Anggota).filter(models.Anggota.status_aktif.is_(True))
    total = aktif_query.count()

    per_golongan = {}
    for golongan in models.GOLONGAN:
        per_golongan[golongan] = (
            aktif_query.filter(models.Anggota.golongan == golongan).count()
        )

    per_kwarcab_rows = (
        db.query(models.Kwarcab.id, models.Kwarcab.nama, models.Anggota.id)
        .join(models.Kwaran, models.Kwaran.kwarcab_id == models.Kwarcab.id)
        .join(models.Gudep, models.Gudep.kwaran_id == models.Kwaran.id)
        .join(models.Anggota, models.Anggota.gudep_id == models.Gudep.id)
        .filter(models.Anggota.status_aktif.is_(True))
        .all()
    )
    per_kwarcab_map = {}
    for kwarcab_id, nama, _ in per_kwarcab_rows:
        entry = per_kwarcab_map.setdefault(kwarcab_id, {"kwarcab_id": kwarcab_id, "nama": nama, "jumlah": 0})
        entry["jumlah"] += 1

    per_kwarcab = sorted(per_kwarcab_map.values(), key=lambda x: x["jumlah"], reverse=True)

    return {"total": total, "per_golongan": per_golongan, "per_kwarcab": per_kwarcab}
