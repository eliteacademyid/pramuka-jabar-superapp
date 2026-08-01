import os
import re
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status

try:
    import cloudinary
    from cloudinary import uploader
except ImportError:  # pragma: no cover - optional dependency
    cloudinary = None
    uploader = None

from sqlalchemy import func, case
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import engine, get_db
from app.deps import get_current_user, get_current_admin
from app.limiter import (
    limiter,
    LIMIT_READ_LIST,
    LIMIT_READ_DETAIL,
    LIMIT_WRITE,
    LIMIT_UPLOAD,
    LIMIT_APPROVAL,
    LIMIT_DASHBOARD,
)

radit_router = APIRouter(tags=["Realisasi"])

# Deteksi dialect sekali saat startup — bukan tiap request
_IS_SQLITE = engine.dialect.name == "sqlite"

# ─── Konstanta keamanan upload ────────────────────────────────────────────────
_MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB

# Whitelist ekstensi yang diizinkan
_ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".jpg", ".jpeg", ".png", ".gif",
    ".zip", ".rar", ".txt", ".csv",
}

# Regex untuk sanitasi nama file — hanya alphanumeric, titik, underscore, dan dash
_SAFE_FILENAME_RE = re.compile(r"[^\w.\-]")


def _safe_filename(user_id: int, original: str) -> str:
    """Sanitasi nama file: strip path traversal, karakter berbahaya, prefix user_id."""
    # Ambil basename saja — cegah path traversal seperti ../../etc/passwd
    basename = Path(original).name
    # Ganti semua karakter tidak aman dengan underscore
    sanitized = _SAFE_FILENAME_RE.sub("_", basename)
    return f"{user_id}_{sanitized}"


def _month_expr(col):
    """Ekspresi grouping bulanan yang kompatibel SQLite dan PostgreSQL."""
    if _IS_SQLITE:
        return func.strftime("%Y-%m", col)
    return func.to_char(col, "YYYY-MM")


# ─── Realisasi ─────────────────────────────────────────────────────────────────

@radit_router.get("/realisasi", response_model=List[schemas.RealisasiResponse])
@limiter.limit(LIMIT_READ_LIST)
def list_realisasi(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    status: Optional[str] = Query(None, max_length=20),
    db: Session = Depends(get_db),
):
    """Get all realisasi entries. Limit: 60/menit per IP."""
    query = db.query(models.Realisasi)

    if search:
        query = query.filter(models.Realisasi.judul.ilike(f"%{search}%"))
    if status:
        query = query.filter(models.Realisasi.status == status)

    query = query.options(selectinload(models.Realisasi.documents))
    return query.order_by(models.Realisasi.created_at.desc()).offset(skip).limit(limit).all()


@radit_router.post("/realisasi", response_model=schemas.RealisasiResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_WRITE)
def create_realisasi(
    request: Request,
    payload: schemas.RealisasiCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a draft realisasi entry. Limit: 30/menit per IP."""
    if payload.program_id is not None:
        exists = db.query(
            db.query(models.Program).filter(models.Program.id == payload.program_id).exists()
        ).scalar()
        if not exists:
            raise HTTPException(status_code=400, detail="Program tidak ditemukan")

    if payload.kegiatan_id is not None:
        exists = db.query(
            db.query(models.Kegiatan).filter(models.Kegiatan.id == payload.kegiatan_id).exists()
        ).scalar()
        if not exists:
            raise HTTPException(status_code=400, detail="Kegiatan tidak ditemukan")

    realisasi = models.Realisasi(
        judul=payload.judul,
        deskripsi=payload.deskripsi,
        target=payload.target,
        realisasi=payload.realisasi,
        periode=payload.periode,
        status=payload.status.value if payload.status else "draft",
        program_id=payload.program_id,
        kegiatan_id=payload.kegiatan_id,
        created_by_id=current_user.id,
    )
    db.add(realisasi)
    db.commit()
    db.refresh(realisasi)
    return realisasi


# ─── Upload ────────────────────────────────────────────────────────────────────

@radit_router.post("/upload", tags=["Realisasi"])
@limiter.limit(LIMIT_UPLOAD)
def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    """Upload a file. Max 10MB. Tipe yang diizinkan: PDF, Word, Excel, gambar, ZIP, CSV. Limit: 10/menit per IP."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid")

    ext = Path(file.filename).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipe file tidak diizinkan. Gunakan: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    content = file.file.read()

    if not content:
        raise HTTPException(status_code=400, detail="File kosong")

    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Ukuran file melebihi batas maksimal {_MAX_UPLOAD_BYTES // 1024 // 1024}MB",
        )

    stored_name = _safe_filename(current_user.id, file.filename)

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret and cloudinary and uploader:
        cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
        try:
            upload_result = uploader.upload(content, resource_type="auto", public_id=stored_name)
            return {
                "filename": file.filename,
                "url": upload_result.get("secure_url") or upload_result.get("url"),
                "message": "File berhasil diupload ke Cloudinary",
            }
        except Exception:
            # Jangan bocorkan detail error Cloudinary ke client
            raise HTTPException(status_code=500, detail="Upload file gagal, coba beberapa saat lagi")

    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / stored_name).write_bytes(content)

    return {
        "filename": file.filename,
        "url": f"/uploads/{stored_name}",
        "message": "File berhasil disimpan",
    }


# ─── Laporan ───────────────────────────────────────────────────────────────────

@radit_router.get("/laporan", response_model=List[schemas.LaporanResponse])
@limiter.limit(LIMIT_READ_LIST)
def list_laporan(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, max_length=20),
    db: Session = Depends(get_db),
):
    """Get all laporan entries. Limit: 60/menit per IP."""
    query = db.query(models.Laporan)
    if status:
        query = query.filter(models.Laporan.status == status)
    return query.order_by(models.Laporan.created_at.desc()).offset(skip).limit(limit).all()


@radit_router.post("/laporan", response_model=schemas.LaporanResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_WRITE)
def create_laporan(
    request: Request,
    payload: schemas.LaporanCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a laporan entry. Limit: 30/menit per IP."""
    if payload.realisasi_id is not None:
        exists = db.query(
            db.query(models.Realisasi).filter(models.Realisasi.id == payload.realisasi_id).exists()
        ).scalar()
        if not exists:
            raise HTTPException(status_code=400, detail="Realisasi tidak ditemukan")

    laporan = models.Laporan(
        judul=payload.judul,
        periode=payload.periode,
        deskripsi=payload.deskripsi,
        status=payload.status.value if payload.status else "draft",
        realisasi_id=payload.realisasi_id,
        created_by_id=current_user.id,
    )
    db.add(laporan)
    db.commit()
    db.refresh(laporan)
    return laporan


# ─── Approval — hanya admin yang boleh approve/reject ─────────────────────────

@radit_router.post("/approval", response_model=schemas.ApprovalResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_APPROVAL)
def process_approval(
    request: Request,
    payload: schemas.ApprovalCreate,
    # get_current_admin memastikan hanya admin yang bisa approve/reject
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Approve or reject a laporan entry. Hanya admin. Limit: 30/menit per IP."""
    laporan = db.query(models.Laporan).filter(models.Laporan.id == payload.laporan_id).first()
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    if laporan.status == "approved":
        raise HTTPException(status_code=400, detail="Laporan yang sudah disetujui tidak dapat diubah lagi")

    laporan.status = payload.status.value
    laporan.approved_by_id = current_user.id

    approval = models.Approval(
        laporan_id=laporan.id,
        user_id=current_user.id,
        status=payload.status.value,
        catatan=payload.catatan,
    )
    db.add(approval)
    db.flush()
    db.commit()
    return approval


# ─── Dashboard — hanya user terautentikasi ─────────────────────────────────────

@radit_router.get("/dashboard/statistik", response_model=schemas.DashboardStatsResponse)
@limiter.limit(LIMIT_DASHBOARD)
def dashboard_statistik(
    request: Request,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Statistik dashboard. Memerlukan autentikasi. Limit: 30/menit per IP."""
    row = db.query(
        func.count(models.Laporan.id).label("total_laporan"),
        func.sum(case((models.Laporan.status == "approved", 1), else_=0)).label("total_disetujui"),
        func.sum(
            case((models.Laporan.status.in_(["draft", "submitted"]), 1), else_=0)
        ).label("total_pending"),
    ).first()

    total_realisasi = db.query(func.count(models.Realisasi.id)).scalar()

    return {
        "total_realisasi": total_realisasi or 0,
        "total_laporan": row.total_laporan or 0,
        "total_disetujui": row.total_disetujui or 0,
        "total_pending": row.total_pending or 0,
    }


@radit_router.get("/dashboard/grafik", response_model=List[schemas.DashboardChartPoint])
@limiter.limit(LIMIT_DASHBOARD)
def dashboard_grafik(
    request: Request,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Data grafik bulanan. Memerlukan autentikasi. Limit: 30/menit per IP."""
    month_expr_laporan = _month_expr(models.Laporan.created_at)
    month_expr_realisasi = _month_expr(models.Realisasi.created_at)

    laporan_rows = (
        db.query(month_expr_laporan.label("bulan"), func.count(models.Laporan.id).label("total"))
        .filter(models.Laporan.created_at.isnot(None))
        .group_by(month_expr_laporan)
        .all()
    )
    realisasi_rows = (
        db.query(month_expr_realisasi.label("bulan"), func.count(models.Realisasi.id).label("total"))
        .filter(models.Realisasi.created_at.isnot(None))
        .group_by(month_expr_realisasi)
        .all()
    )

    grouped: dict = {}
    for row in laporan_rows:
        grouped.setdefault(row.bulan, {"bulan": row.bulan, "total_laporan": 0, "total_realisasi": 0})
        grouped[row.bulan]["total_laporan"] = row.total
    for row in realisasi_rows:
        grouped.setdefault(row.bulan, {"bulan": row.bulan, "total_laporan": 0, "total_realisasi": 0})
        grouped[row.bulan]["total_realisasi"] = row.total

    return [grouped[k] for k in sorted(grouped)]


@radit_router.get("/dashboard/perbandingan", response_model=schemas.DashboardComparisonResponse)
@limiter.limit(LIMIT_DASHBOARD)
def dashboard_perbandingan(
    request: Request,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Perbandingan target vs realisasi. Memerlukan autentikasi. Limit: 30/menit per IP."""
    totals = db.query(
        func.coalesce(func.sum(models.Realisasi.target), 0).label("target_sum"),
        func.coalesce(func.sum(models.Realisasi.realisasi), 0).label("realisasi_sum"),
    ).first()

    target_sum = int(totals.target_sum or 0)
    realisasi_sum = int(totals.realisasi_sum or 0)

    return {
        "target": target_sum,
        "realisasi": realisasi_sum,
        "selisih": realisasi_sum - target_sum,
        "persentase": round((realisasi_sum / target_sum) * 100, 2) if target_sum else 0.0,
    }
