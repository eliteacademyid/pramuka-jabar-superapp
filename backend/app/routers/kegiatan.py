import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin, get_current_user, get_current_user_or_pj

router = APIRouter(prefix="/kegiatan", tags=["kegiatan"], redirect_slashes=False)

UPLOAD_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "kegiatan")
)
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _get_kegiatan_or_404(db: Session, kegiatan_id: int) -> models.Kegiatan:
    kegiatan = (
        db.query(models.Kegiatan)
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )
    if not kegiatan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kegiatan tidak ditemukan"
        )
    return kegiatan


def _validate_kegiatan_payload(payload: schemas.KegiatanCreate) -> None:
    if payload.tanggal_selesai < payload.tanggal_mulai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tanggal selesai tidak boleh lebih awal dari tanggal mulai",
        )
    if not payload.nama_kegiatan.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nama kegiatan tidak boleh kosong",
        )


def _validate_file(file: UploadFile) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in models.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipe file tidak diizinkan. Format yang diperbolehkan: PDF, JPG, PNG, DOCX",
        )
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > models.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ukuran file maksimal 5MB",
        )


@router.get("/stats", response_model=schemas.KegiatanStats)
def get_stats(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    total = db.query(models.Kegiatan).count()
    berlangsung = (
        db.query(models.Kegiatan)
        .filter(models.Kegiatan.status == "berlangsung")
        .count()
    )
    selesai = (
        db.query(models.Kegiatan)
        .filter(models.Kegiatan.status == "selesai")
        .count()
    )
    return schemas.KegiatanStats(
        total_kegiatan=total,
        kegiatan_berlangsung=berlangsung,
        kegiatan_selesai=selesai,
    )


@router.get("", response_model=List[schemas.KegiatanOut])
def list_kegiatan(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    kegiatan_list = (
        db.query(models.Kegiatan)
        .order_by(models.Kegiatan.tanggal_mulai.desc())
        .all()
    )
    for k in kegiatan_list:
        if k.penanggung_jawab_id:
            user = db.query(models.User).filter(models.User.id == k.penanggung_jawab_id).first()
            if user:
                k.penanggung_jawab = user
    return kegiatan_list


@router.get("/{kegiatan_id}", response_model=schemas.KegiatanOut)
def get_kegiatan(
    kegiatan_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    kegiatan = _get_kegiatan_or_404(db, kegiatan_id)
    if kegiatan.penanggung_jawab_id:
        user = db.query(models.User).filter(models.User.id == kegiatan.penanggung_jawab_id).first()
        if user:
            kegiatan.penanggung_jawab = user
    dok = (
        db.query(models.DokumentasiKegiatan)
        .filter(models.DokumentasiKegiatan.kegiatan_id == kegiatan_id)
        .first()
    )
    kegiatan.dokumentasi = dok
    return kegiatan


@router.post("", response_model=schemas.KegiatanOut, status_code=status.HTTP_201_CREATED)
def create_kegiatan(
    payload: schemas.KegiatanCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _validate_kegiatan_payload(payload)
    user = db.query(models.User).filter(models.User.id == payload.penanggung_jawab_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Penanggung jawab tidak ditemukan",
        )
    kegiatan = models.Kegiatan(
        nama_kegiatan=payload.nama_kegiatan.strip(),
        deskripsi=payload.deskripsi,
        tanggal_mulai=payload.tanggal_mulai,
        tanggal_selesai=payload.tanggal_selesai,
        penanggung_jawab_id=payload.penanggung_jawab_id,
    )
    db.add(kegiatan)
    db.commit()
    db.refresh(kegiatan)
    if kegiatan.penanggung_jawab_id:
        kegiatan.penanggung_jawab = user
    return kegiatan


@router.put("/{kegiatan_id}", response_model=schemas.KegiatanOut)
def update_kegiatan(
    kegiatan_id: int,
    payload: schemas.KegiatanUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    kegiatan = _get_kegiatan_or_404(db, kegiatan_id)

    if payload.nama_kegiatan is not None:
        kegiatan.nama_kegiatan = payload.nama_kegiatan.strip()
    if payload.deskripsi is not None:
        kegiatan.deskripsi = payload.deskripsi
    if payload.tanggal_mulai is not None:
        kegiatan.tanggal_mulai = payload.tanggal_mulai
    if payload.tanggal_selesai is not None:
        kegiatan.tanggal_selesai = payload.tanggal_selesai
    if payload.penanggung_jawab_id is not None:
        user = db.query(models.User).filter(models.User.id == payload.penanggung_jawab_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Penanggung jawab tidak ditemukan",
            )
        kegiatan.penanggung_jawab_id = payload.penanggung_jawab_id

    if kegiatan.tanggal_selesai < kegiatan.tanggal_mulai:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tanggal selesai tidak boleh lebih awal dari tanggal mulai",
        )

    db.commit()
    db.refresh(kegiatan)
    if kegiatan.penanggung_jawab_id:
        user = db.query(models.User).filter(models.User.id == kegiatan.penanggung_jawab_id).first()
        if user:
            kegiatan.penanggung_jawab = user
    return kegiatan


@router.delete("/{kegiatan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kegiatan(
    kegiatan_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    kegiatan = _get_kegiatan_or_404(db, kegiatan_id)
    dok = (
        db.query(models.DokumentasiKegiatan)
        .filter(models.DokumentasiKegiatan.kegiatan_id == kegiatan_id)
        .first()
    )
    if dok:
        for file in dok.files:
            file_path = os.path.join(UPLOAD_DIR, file.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.delete(dok)
    db.delete(kegiatan)
    db.commit()


@router.patch("/{kegiatan_id}/status", response_model=schemas.KegiatanOut)
def update_status(
    kegiatan_id: int,
    payload: schemas.StatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_pj),
):
    if payload.status not in models.STATUS_KEGIATAN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status tidak valid. Gunakan: {', '.join(models.STATUS_KEGIATAN)}",
        )
    kegiatan = _get_kegiatan_or_404(db, kegiatan_id)
    kegiatan.status = payload.status
    db.commit()
    db.refresh(kegiatan)
    if kegiatan.penanggung_jawab_id:
        user = db.query(models.User).filter(models.User.id == kegiatan.penanggung_jawab_id).first()
        if user:
            kegiatan.penanggung_jawab = user
    return kegiatan


@router.put("/{kegiatan_id}/dokumentasi", response_model=schemas.DokumentasiOut)
def update_dokumentasi(
    kegiatan_id: int,
    payload: schemas.DokumentasiUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_pj),
):
    _get_kegiatan_or_404(db, kegiatan_id)
    dok = (
        db.query(models.DokumentasiKegiatan)
        .filter(models.DokumentasiKegiatan.kegiatan_id == kegiatan_id)
        .first()
    )
    if not dok:
        dok = models.DokumentasiKegiatan(
            kegiatan_id=kegiatan_id, catatan=payload.catatan
        )
        db.add(dok)
    else:
        dok.catatan = payload.catatan
    db.commit()
    db.refresh(dok)
    return dok


@router.post(
    "/{kegiatan_id}/dokumentasi/files",
    response_model=schemas.FileDokumentasiOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file_dokumentasi(
    kegiatan_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_pj),
):
    _get_kegiatan_or_404(db, kegiatan_id)
    _validate_file(file)

    ext = os.path.splitext(file.filename or ".bin")[1].lower()
    hashed_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, hashed_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    dok = (
        db.query(models.DokumentasiKegiatan)
        .filter(models.DokumentasiKegiatan.kegiatan_id == kegiatan_id)
        .first()
    )
    if not dok:
        dok = models.DokumentasiKegiatan(kegiatan_id=kegiatan_id)
        db.add(dok)
        db.flush()

    file_record = models.FileDokumentasi(
        dokumentasi_id=dok.id,
        nama_file=file.filename or "file",
        file_path=hashed_name,
        ukuran=len(content),
        tipe_file=file.content_type or "application/octet-stream",
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record


@router.delete("/{kegiatan_id}/dokumentasi/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file_dokumentasi(
    kegiatan_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_or_pj),
):
    file_record = (
        db.query(models.FileDokumentasi)
        .filter(models.FileDokumentasi.id == file_id)
        .first()
    )
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File tidak ditemukan"
        )
    file_path = os.path.join(UPLOAD_DIR, file_record.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(file_record)
    db.commit()


@router.get("/{kegiatan_id}/dokumentasi/files/{file_id}")
def download_file_dokumentasi(
    kegiatan_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    file_record = (
        db.query(models.FileDokumentasi)
        .filter(models.FileDokumentasi.id == file_id)
        .first()
    )
    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File tidak ditemukan"
        )
    file_path = os.path.join(UPLOAD_DIR, file_record.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File tidak ditemukan di server"
        )
    return FileResponse(
        path=file_path,
        filename=file_record.nama_file,
        media_type=file_record.tipe_file,
    )
