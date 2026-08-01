import os
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

try:
    import cloudinary
    from cloudinary import uploader
except ImportError:  # pragma: no cover - optional dependency
    cloudinary = None
    uploader = None

from sqlalchemy import func, case, text
from sqlalchemy.orm import Session, selectinload

from app import models, schemas
from app.database import engine, get_db
from app.deps import get_current_user

radit_router = APIRouter(tags=["Realisasi"])

# Deteksi dialect sekali saat startup — bukan tiap request
_IS_SQLITE = engine.dialect.name == "sqlite"


def _month_expr(col):
    """Ekspresi grouping bulanan yang kompatibel SQLite dan PostgreSQL."""
    if _IS_SQLITE:
        return func.strftime("%Y-%m", col)
    return func.to_char(col, "YYYY-MM")


# ─── Realisasi ─────────────────────────────────────────────────────────────────

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

    # selectinload documents: satu IN query untuk semua dokumen sekaligus,
    # bukan N query lazy-load per baris (N+1 problem)
    query = query.options(selectinload(models.Realisasi.documents))

    return query.order_by(models.Realisasi.created_at.desc()).offset(skip).limit(limit).all()


@radit_router.post("/realisasi", response_model=schemas.RealisasiResponse, status_code=status.HTTP_201_CREATED)
def create_realisasi(
    payload: schemas.RealisasiCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a draft realisasi entry."""
    if not payload.judul or not payload.judul.strip():
        raise HTTPException(status_code=400, detail="Judul realisasi tidak boleh kosong")

    # EXISTS lebih ringan dari SELECT * — tidak fetch semua kolom
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
        status=payload.status or "draft",
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
def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    """Upload a file to Cloudinary when configured, otherwise store it locally."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak valid")

    stored_name = f"{current_user.id}_{file.filename.replace(' ', '_')}"
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File kosong")

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
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Upload ke Cloudinary gagal: {exc}") from exc

    upload_dir = Path(__file__).resolve().parent.parent / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / stored_name).write_bytes(content)

    return {
        "filename": file.filename,
        "url": f"/uploads/{stored_name}",
        "message": "File berhasil disimpan secara lokal karena Cloudinary belum dikonfigurasi",
    }


# ─── Laporan ───────────────────────────────────────────────────────────────────

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

    # EXISTS — tidak perlu fetch semua kolom realisasi
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
        status=payload.status or "draft",
        realisasi_id=payload.realisasi_id,
        created_by_id=current_user.id,
    )
    db.add(laporan)
    db.commit()
    db.refresh(laporan)
    return laporan


# ─── Approval ──────────────────────────────────────────────────────────────────

@radit_router.post("/approval", response_model=schemas.ApprovalResponse, status_code=status.HTTP_201_CREATED)
def process_approval(
    payload: schemas.ApprovalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Approve or reject a laporan entry."""
    if payload.status not in {"approved", "rejected"}:
        raise HTTPException(status_code=400, detail="Status approval tidak valid")

    laporan = db.query(models.Laporan).filter(models.Laporan.id == payload.laporan_id).first()
    if not laporan:
        raise HTTPException(status_code=404, detail="Laporan tidak ditemukan")
    if laporan.status == "approved":
        raise HTTPException(status_code=400, detail="Laporan yang sudah disetujui tidak dapat diubah lagi")

    # Update laporan dan buat approval dalam satu transaksi
    laporan.status = payload.status
    laporan.approved_by_id = current_user.id

    approval = models.Approval(
        laporan_id=laporan.id,
        user_id=current_user.id,
        status=payload.status,
        catatan=payload.catatan,
    )
    db.add(approval)
    db.flush()   # flush agar approval.id tersedia tanpa round-trip commit dulu
    db.commit()

    # Return langsung dari object yang sudah di-flush — tidak perlu db.refresh()
    return approval


# ─── Dashboard ─────────────────────────────────────────────────────────────────

@radit_router.get("/dashboard/statistik", response_model=schemas.DashboardStatsResponse)
def dashboard_statistik(db: Session = Depends(get_db)):
    """Get card statistics — satu query agregasi untuk laporan, satu untuk realisasi."""
    # Satu query conditional aggregation untuk semua stat laporan
    row = db.query(
        func.count(models.Laporan.id).label("total_laporan"),
        func.sum(case((models.Laporan.status == "approved", 1), else_=0)).label("total_disetujui"),
        func.sum(
            case((models.Laporan.status.in_(["draft", "submitted"]), 1), else_=0)
        ).label("total_pending"),
    ).first()

    # COUNT(*) langsung dari index PK — paling cepat
    total_realisasi = db.query(func.count(models.Realisasi.id)).scalar()

    return {
        "total_realisasi": total_realisasi or 0,
        "total_laporan": row.total_laporan or 0,
        "total_disetujui": row.total_disetujui or 0,
        "total_pending": row.total_pending or 0,
    }


@radit_router.get("/dashboard/grafik", response_model=List[schemas.DashboardChartPoint])
def dashboard_grafik(db: Session = Depends(get_db)):
    """Get chart data for monthly progress — kompatibel SQLite & PostgreSQL."""
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
def dashboard_perbandingan(db: Session = Depends(get_db)):
    """Compare target vs realisasi values."""
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
