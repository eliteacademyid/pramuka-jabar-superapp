import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/lampiran", tags=["lampiran"])

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _get_upload_dir() -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return UPLOAD_DIR


@router.post("", response_model=schemas.LampiranOut, status_code=status.HTTP_201_CREATED)
async def upload_lampiran(
    surat_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Validasi surat ada
    surat = db.query(models.Surat).filter(models.Surat.id == surat_id).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat tidak ditemukan")

    # Validasi ekstensi
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipe file tidak diizinkan. Gunakan: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Baca dan validasi ukuran
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 10 MB")

    # Simpan file dengan nama unik
    unique_name = f"{uuid.uuid4().hex}{ext.lower()}"
    upload_dir = _get_upload_dir()
    file_path = os.path.join(upload_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    lampiran = models.Lampiran(
        surat_id=surat_id,
        nama_file=file.filename,
        lokasi_file=file_path,
        ukuran_file=len(content),
        tipe_file=ext.lower(),
    )
    db.add(lampiran)

    # Audit log
    log = models.AuditLog(
        surat_id=surat_id,
        user_id=current_user.id,
        aktivitas="Lampiran Diunggah",
        keterangan=file.filename,
    )
    db.add(log)
    db.commit()
    db.refresh(lampiran)
    return lampiran


@router.get("/{lampiran_id}/download")
def download_lampiran(
    lampiran_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    lampiran = db.query(models.Lampiran).filter(models.Lampiran.id == lampiran_id).first()
    if not lampiran:
        raise HTTPException(status_code=404, detail="Lampiran tidak ditemukan")
    if not os.path.exists(lampiran.lokasi_file):
        raise HTTPException(status_code=404, detail="File tidak ditemukan di server")
    return FileResponse(
        path=lampiran.lokasi_file,
        filename=lampiran.nama_file,
        media_type="application/octet-stream",
    )


@router.delete("/{lampiran_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lampiran(
    lampiran_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    lampiran = db.query(models.Lampiran).filter(models.Lampiran.id == lampiran_id).first()
    if not lampiran:
        raise HTTPException(status_code=404, detail="Lampiran tidak ditemukan")

    # Hapus file fisik
    if os.path.exists(lampiran.lokasi_file):
        os.remove(lampiran.lokasi_file)

    db.delete(lampiran)
    db.commit()
