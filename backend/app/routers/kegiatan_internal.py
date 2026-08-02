import os
import uuid
from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.config import UPLOAD_DIR
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["kegiatan-internal"])


def _cek_status(status: str):
    if status not in models.PROGRAM_STATUS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Status tidak valid"
        )


def _get_bidang_or_404(db: Session, bidang_id: int) -> models.BidangKwarda:
    obj = db.query(models.BidangKwarda).filter(models.BidangKwarda.id == bidang_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Bidang tidak ditemukan")
    return obj


def _get_program_or_404(db: Session, pk_id: int) -> models.ProgramKerja:
    obj = db.query(models.ProgramKerja).filter(models.ProgramKerja.id == pk_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Program kerja tidak ditemukan")
    return obj


def _get_kegiatan_or_404(db: Session, kegiatan_id: int) -> models.Kegiatan:
    obj = db.query(models.Kegiatan).filter(models.Kegiatan.id == kegiatan_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    return obj


def _validasi_tanggal(mulai: date, selesai: Optional[date]):
    if selesai and selesai < mulai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tanggal selesai tidak boleh lebih awal dari tanggal mulai",
        )


def _validasi_program_kerja(db: Session, pk_id: Optional[int]):
    if pk_id is not None:
        _get_program_or_404(db, pk_id)


# ---------- Bidang Kwarda ----------


@router.get("/bidang-kwarda", response_model=List[schemas.BidangKwardaOut])
def list_bidang(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return db.query(models.BidangKwarda).order_by(models.BidangKwarda.nama_bidang).all()


@router.post(
    "/bidang-kwarda",
    response_model=schemas.BidangKwardaOut,
    status_code=status.HTTP_201_CREATED,
)
def create_bidang(
    payload: schemas.BidangKwardaCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if db.query(models.BidangKwarda).filter(
        models.BidangKwarda.nama_bidang == payload.nama_bidang
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nama bidang sudah ada"
        )
    obj = models.BidangKwarda(nama_bidang=payload.nama_bidang)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bidang-kwarda/{bidang_id}", response_model=schemas.BidangKwardaOut)
def update_bidang(
    bidang_id: int,
    payload: schemas.BidangKwardaUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_bidang_or_404(db, bidang_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("nama_bidang"):
        existing = (
            db.query(models.BidangKwarda)
            .filter(models.BidangKwarda.nama_bidang == data["nama_bidang"])
            .first()
        )
        if existing and existing.id != bidang_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Nama bidang sudah ada"
            )
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/bidang-kwarda/{bidang_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bidang(
    bidang_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_bidang_or_404(db, bidang_id)
    if (
        db.query(models.ProgramKerja)
        .filter(models.ProgramKerja.bidang_id == bidang_id)
        .count()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa dihapus: masih ada program kerja pada bidang ini",
        )
    db.delete(obj)
    db.commit()


# ---------- Program Kerja ----------


@router.get("/program-kerja")
def list_program_kerja(
    bidang_id: Optional[int] = Query(default=None),
    tahun: Optional[int] = Query(default=None),
    status_: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.ProgramKerja).options(
        joinedload(models.ProgramKerja.bidang)
    )
    if bidang_id is not None:
        query = query.filter(models.ProgramKerja.bidang_id == bidang_id)
    if tahun is not None:
        query = query.filter(models.ProgramKerja.tahun == tahun)
    if status_:
        query = query.filter(models.ProgramKerja.status == status_)
    rows = query.order_by(models.ProgramKerja.tahun.desc(), models.ProgramKerja.id.desc()).all()
    return [
        {
            **schemas.ProgramKerjaOut.model_validate(p).model_dump(),
            "nama_bidang": p.bidang.nama_bidang if p.bidang else "",
        }
        for p in rows
    ]


@router.get("/program-kerja/rekap")
def rekap_program_kerja(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    per_status = {}
    for s in models.PROGRAM_STATUS:
        per_status[s] = (
            db.query(models.ProgramKerja).filter(models.ProgramKerja.status == s).count()
        )

    rows = (
        db.query(models.BidangKwarda.id, models.BidangKwarda.nama_bidang, models.ProgramKerja.id)
        .join(models.ProgramKerja, models.ProgramKerja.bidang_id == models.BidangKwarda.id)
        .all()
    )
    per_bidang_map = {}
    for bidang_id, nama, _ in rows:
        entry = per_bidang_map.setdefault(
            bidang_id, {"bidang_id": bidang_id, "nama_bidang": nama, "jumlah": 0}
        )
        entry["jumlah"] += 1
    per_bidang = sorted(per_bidang_map.values(), key=lambda x: x["jumlah"], reverse=True)

    total = db.query(models.ProgramKerja).count()
    return {"total": total, "per_status": per_status, "per_bidang": per_bidang}


@router.post(
    "/program-kerja",
    response_model=schemas.ProgramKerjaOut,
    status_code=status.HTTP_201_CREATED,
)
def create_program_kerja(
    payload: schemas.ProgramKerjaCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_bidang_or_404(db, payload.bidang_id)
    _cek_status(payload.status)
    obj = models.ProgramKerja(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/program-kerja/{pk_id}", response_model=schemas.ProgramKerjaOut)
def update_program_kerja(
    pk_id: int,
    payload: schemas.ProgramKerjaUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_program_or_404(db, pk_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("bidang_id"):
        _get_bidang_or_404(db, data["bidang_id"])
    if data.get("status"):
        _cek_status(data["status"])
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/program-kerja/{pk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program_kerja(
    pk_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_program_or_404(db, pk_id)
    if (
        db.query(models.Kegiatan)
        .filter(models.Kegiatan.program_kerja_id == pk_id)
        .count()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa dihapus: masih ada kegiatan pada program kerja ini",
        )
    db.delete(obj)
    db.commit()


# ---------- Kegiatan ----------


def _serialize_kegiatan(k: models.Kegiatan) -> dict:
    data = schemas.KegiatanOut.model_validate(k).model_dump()
    data["judul_program_kerja"] = (
        k.program_kerja.judul if k.program_kerja else None
    )
    data["dokumen"] = [
        schemas.KegiatanDokumenOut.model_validate(d).model_dump()
        for d in k.dokumen
    ]
    return data


@router.get("/kegiatan")
def list_kegiatan(
    program_kerja_id: Optional[int] = Query(default=None),
    status_: Optional[str] = Query(default=None, alias="status"),
    tanggal_mulai: Optional[date] = Query(default=None),
    tanggal_selesai: Optional[date] = Query(default=None),
    q: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.Kegiatan).options(
        joinedload(models.Kegiatan.program_kerja),
        joinedload(models.Kegiatan.dokumen),
    )
    if program_kerja_id is not None:
        query = query.filter(models.Kegiatan.program_kerja_id == program_kerja_id)
    if status_:
        query = query.filter(models.Kegiatan.status == status_)
    if tanggal_mulai:
        query = query.filter(models.Kegiatan.tanggal_mulai >= tanggal_mulai)
    if tanggal_selesai:
        query = query.filter(models.Kegiatan.tanggal_mulai <= tanggal_selesai)
    if q:
        query = query.filter(models.Kegiatan.judul.ilike(f"%{q}%"))
    rows = query.order_by(models.Kegiatan.tanggal_mulai.asc(), models.Kegiatan.id.asc()).all()
    return [_serialize_kegiatan(k) for k in rows]


@router.get("/kegiatan/mendatang")
def kegiatan_mendatang(
    limit: int = Query(default=5, ge=1, le=10),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    today = date.today()
    rows = (
        db.query(models.Kegiatan)
        .options(joinedload(models.Kegiatan.program_kerja))
        .filter(
            models.Kegiatan.tanggal_mulai >= today,
            models.Kegiatan.status.in_(["rencana", "berjalan"]),
        )
        .order_by(models.Kegiatan.tanggal_mulai.asc())
        .limit(limit)
        .all()
    )
    result = []
    for k in rows:
        data = schemas.KegiatanOut.model_validate(k).model_dump()
        data["judul_program_kerja"] = (
            k.program_kerja.judul if k.program_kerja else None
        )
        result.append(data)
    return result


@router.get("/kegiatan/{kegiatan_id}")
def get_kegiatan(
    kegiatan_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    k = (
        db.query(models.Kegiatan)
        .options(
            joinedload(models.Kegiatan.program_kerja),
            joinedload(models.Kegiatan.dokumen),
        )
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )
    if not k:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    return _serialize_kegiatan(k)


@router.post(
    "/kegiatan",
    response_model=schemas.KegiatanOut,
    status_code=status.HTTP_201_CREATED,
)
def create_kegiatan(
    payload: schemas.KegiatanCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _validasi_program_kerja(db, payload.program_kerja_id)
    _cek_status(payload.status)
    _validasi_tanggal(payload.tanggal_mulai, payload.tanggal_selesai)
    obj = models.Kegiatan(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/kegiatan/{kegiatan_id}", response_model=schemas.KegiatanOut)
def update_kegiatan(
    kegiatan_id: int,
    payload: schemas.KegiatanUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kegiatan_or_404(db, kegiatan_id)
    data = payload.model_dump(exclude_unset=True)
    if "program_kerja_id" in data:
        _validasi_program_kerja(db, data["program_kerja_id"])
    if data.get("status"):
        _cek_status(data["status"])

    mulai = data.get("tanggal_mulai") or obj.tanggal_mulai
    selesai = data.get("tanggal_selesai") if "tanggal_selesai" in data else obj.tanggal_selesai
    _validasi_tanggal(mulai, selesai)

    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/kegiatan/{kegiatan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kegiatan(
    kegiatan_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kegiatan_or_404(db, kegiatan_id)
    for dok in obj.dokumen:
        _hapus_file(dok.file_url)
    db.delete(obj)
    db.commit()


@router.patch("/kegiatan/{kegiatan_id}/status", response_model=schemas.KegiatanOut)
def update_status_kegiatan(
    kegiatan_id: int,
    payload: schemas.KegiatanStatusUpdate,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kegiatan_or_404(db, kegiatan_id)
    _cek_status(payload.status)

    if obj.status == "selesai" and payload.status == "rencana" and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kegiatan sudah selesai. Ubah balik ke rencana perlu konfirmasi (kirim force=true).",
        )

    obj.status = payload.status
    db.commit()
    db.refresh(obj)
    return obj


# ---------- Dokumen Kegiatan ----------


def _hapus_file(file_url: str):
    if not file_url:
        return
    name = file_url.rsplit("/", 1)[-1]
    path = Path(UPLOAD_DIR) / name
    if path.exists():
        path.unlink()


@router.post(
    "/kegiatan/{kegiatan_id}/dokumen",
    response_model=schemas.KegiatanDokumenOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_dokumen(
    kegiatan_id: int,
    tipe: str = Query(default="lainnya"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_kegiatan_or_404(db, kegiatan_id)
    if tipe not in models.DOKUMEN_TIPE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tipe dokumen tidak valid"
        )

    ext = Path(file.filename or "").suffix.lower()
    if ext not in models.DOKUMEN_EXT_IZIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipe file tidak diizinkan (pdf, jpg, png, docx)",
        )

    ukuran = 0
    chunk_size = 1024 * 1024
    potongan = []
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        ukuran += len(chunk)
        potongan.append(chunk)
        if ukuran > models.DOKUMEN_MAX_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ukuran file melebihi {models.DOKUMEN_MAX_MB} MB",
            )

    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    nama_tersimpan = f"{uuid.uuid4().hex}{ext}"
    tujuan = Path(UPLOAD_DIR) / nama_tersimpan
    with open(tujuan, "wb") as out:
        for chunk in potongan:
            out.write(chunk)

    nama_file = file.filename or nama_tersimpan
    obj = models.KegiatanDokumen(
        kegiatan_id=kegiatan_id,
        nama_file=nama_file,
        file_url=f"/uploads/{nama_tersimpan}",
        tipe=tipe,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete(
    "/kegiatan/{kegiatan_id}/dokumen/{dokumen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_dokumen(
    kegiatan_id: int,
    dokumen_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_kegiatan_or_404(db, kegiatan_id)
    dok = (
        db.query(models.KegiatanDokumen)
        .filter(
            models.KegiatanDokumen.id == dokumen_id,
            models.KegiatanDokumen.kegiatan_id == kegiatan_id,
        )
        .first()
    )
    if not dok:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    _hapus_file(dok.file_url)
    db.delete(dok)
    db.commit()
