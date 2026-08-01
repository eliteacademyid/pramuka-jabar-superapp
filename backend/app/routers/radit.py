import os
from pathlib import Path
from typing import List, Optional

import cloudinary
from cloudinary import uploader
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

radit_router = APIRouter(tags=["Realisasi"])


@radit_router.get("/realisasi", response_model=List[schemas.RealisasiResponse])
def list_realisasi(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get all realisasi entries."""
    query = db.query(models.Realisasi)

    if search:
        query = query.filter(models.Realisasi.judul.ilike(f"%{search}%"))
    if status:
        query = query.filter(models.Realisasi.status == status)

    realisasi = query.order_by(models.Realisasi.created_at.desc()).offset(skip).limit(limit).all()
    return realisasi


@radit_router.post("/realisasi", response_model=schemas.RealisasiResponse, status_code=status.HTTP_201_CREATED)
def create_realisasi(
    payload: schemas.RealisasiCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a draft realisasi entry."""
    if not payload.judul or not payload.judul.strip():
        raise HTTPException(status_code=400, detail="Judul realisasi tidak boleh kosong")

    if payload.program_id is not None:
        program = db.query(models.Program).filter(models.Program.id == payload.program_id).first()
        if not program:
            raise HTTPException(status_code=400, detail="Program tidak ditemukan")

    if payload.kegiatan_id is not None:
        kegiatan = db.query(models.Kegiatan).filter(models.Kegiatan.id == payload.kegiatan_id).first()
        if not kegiatan:
            raise HTTPException(status_code=400, detail="Kegiatan tidak ditemukan")

    realisasi = models.Realisasi(
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        target=payload.target,
        realisasi=payload.realisasi,
        periode=payload.periode,
        status=payload.status or "draft",
        program_id=payload.program_id,
        kegiatan_id=payload.kegiatan_id,
        created_by_id=current_user.id,
    )
    db.add(realisasi)
    db.commit()
    db.refresh(realisasi)
    return realisasi


@radit_router.post("/upload", tags=["Realisasi"])
def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    """Upload a file to Cloudinary when configured, otherwise store it locally."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid")

    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{current_user.id}_{file.filename.replace(' ', '_')}"
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File kosong")

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret:
        cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
        try:
            upload_result = uploader.upload(content, resource_type="auto", public_id=stored_name)
            return {
                "filename": file.filename,
                "url": upload_result.get("secure_url") or upload_result.get("url"),
                "message": "File berhasil diupload ke Cloudinary",
            }
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Upload ke Cloudinary gagal: {exc}") from exc

    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / stored_name
    target_path.write_bytes(content)

    return {
        "filename": file.filename,
        "url": f"/uploads/{stored_name}",
        "message": "File berhasil disimpan secara lokal karena Cloudinary belum dikonfigurasi",
    }


@radit_router.get("/laporan", response_model=List[schemas.LaporanResponse])
def list_laporan(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get all laporan entries."""
    query = db.query(models.Laporan)
    if status:
        query = query.filter(models.Laporan.status == status)
    return query.order_by(models.Laporan.created_at.desc()).offset(skip).limit(limit).all()


@radit_router.post("/laporan", response_model=schemas.LaporanResponse, status_code=status.HTTP_201_CREATED)
def create_laporan(
    payload: schemas.LaporanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a laporan entry."""
    if not payload.judul or not payload.judul.strip():
        raise HTTPException(status_code=400, detail="Judul laporan tidak boleh kosong")

    if payload.realisasi_id is not None:
        realisasi = db.query(models.Realisasi).filter(models.Realisasi.id == payload.realisasi_id).first()
        if not realisasi:
            raise HTTPException(status_code=400, detail="Realisasi tidak ditemukan")

    laporan = models.Laporan(
        judul=payload.judul,
        periode=payload.periode,
        deskripsi=payload.deskripsi,
        status=payload.status or "draft",
        realisasi_id=payload.realisasi_id,
        created_by_id=current_user.id,
    )
    db.add(laporan)
    db.commit()
    db.refresh(laporan)
    return laporan


@radit_router.post("/approval", response_model=schemas.ApprovalResponse, status_code=status.HTTP_201_CREATED)
def process_approval(
    payload: schemas.ApprovalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve or reject a laporan entry."""
    laporan = db.query(models.Laporan).filter(models.Laporan.id == payload.laporan_id).first()
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    if laporan.status == "approved":
        raise HTTPException(status_code=400, detail="Laporan yang sudah disetujui tidak dapat diubah lagi")

    if payload.status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Status approval tidak valid")

    laporan.status = payload.status
    laporan.approved_by_id = current_user.id

    approval = models.Approval(
        laporan_id=laporan.id,
        user_id=current_user.id,
        status=payload.status,
        catatan=payload.catatan,
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@radit_router.get("/dashboard/statistik", response_model=schemas.DashboardStatsResponse)
def dashboard_statistik(db: Session = Depends(get_db)):
    """Get card statistics for the dashboard."""
    total_realisasi = db.query(models.Realisasi).count()
    total_laporan = db.query(models.Laporan).count()
    total_disetujui = db.query(models.Laporan).filter(models.Laporan.status == "approved").count()
    total_pending = db.query(models.Laporan).filter(models.Laporan.status.in_(["draft", "submitted"])).count()

    return {
        "total_realisasi": total_realisasi,
        "total_laporan": total_laporan,
        "total_disetujui": total_disetujui,
        "total_pending": total_pending,
    }


@radit_router.get("/dashboard/grafik", response_model=List[schemas.DashboardChartPoint])
def dashboard_grafik(db: Session = Depends(get_db)):
    """Get chart data for monthly progress."""
    laporan_rows = db.query(models.Laporan).all()
    realisasi_rows = db.query(models.Realisasi).all()

    grouped = {}
    for row in laporan_rows:
        month_key = row.created_at.strftime("%Y-%m") if row.created_at else "unknown"
        grouped.setdefault(month_key, {"bulan": month_key, "total_laporan": 0, "total_realisasi": 0})
        grouped[month_key]["total_laporan"] += 1

    for row in realisasi_rows:
        month_key = row.created_at.strftime("%Y-%m") if row.created_at else "unknown"
        grouped.setdefault(month_key, {"bulan": month_key, "total_laporan": 0, "total_realisasi": 0})
        grouped[month_key]["total_realisasi"] += 1

    return [grouped[key] for key in sorted(grouped)]


@radit_router.get("/dashboard/perbandingan", response_model=schemas.DashboardComparisonResponse)
def dashboard_perbandingan(db: Session = Depends(get_db)):
    """Compare target vs realisasi values."""
    totals = db.query(
        func.coalesce(func.sum(models.Realisasi.target), 0).label("target_sum"),
        func.coalesce(func.sum(models.Realisasi.realisasi), 0).label("realisasi_sum"),
    ).first()

    target_sum = int(totals.target_sum or 0)
    realisasi_sum = int(totals.realisasi_sum or 0)
    selisih = realisasi_sum - target_sum
    persentase = round((realisasi_sum / target_sum) * 100, 2) if target_sum else 0.0

    return {
        "target": target_sum,
        "realisasi": realisasi_sum,
        "selisih": selisih,
        "persentase": persentase,
    }
