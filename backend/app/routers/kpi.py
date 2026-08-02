"""
Router untuk Dashboard KPI - menampilkan key performance indicators organisasi.

KPI yang ditampilkan:
- Program selesai (%)
- Program terlambat (%)
- Program gagal (%)
- Program aktif (%)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.limiter import limiter, LIMIT_READ_LIST, LIMIT_READ_DETAIL
from app.utils.kpi import (
    get_single_organisasi_kpi,
    get_all_organisasi_kpi,
    get_organisasi_kpi_by_user,
)

router = APIRouter(prefix="/kpi", tags=["Dashboard KPI"])


def _is_admin(user: models.User) -> bool:
    """Cek admin via nama role."""
    return user.role is not None and user.role.name == "admin"


@router.get("/my-organisasi", response_model=schemas.OrganisasiKPIResponse)
@limiter.limit(LIMIT_READ_LIST)
def get_my_organisasi_kpi(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get KPI untuk organisasi user yang sedang login.
    
    Menampilkan:
    - Program selesai (%)
    - Program terlambat (%)
    - Program gagal (%)
    - Program aktif (%)
    
    Limit: 60/menit per IP
    """
    kpi_data = get_organisasi_kpi_by_user(db, current_user.id)
    
    if kpi_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User tidak memiliki organisasi yang terkait",
        )
    
    return schemas.OrganisasiKPIResponse(**kpi_data)


@router.get("/organisasi/{organisasi_id}", response_model=schemas.OrganisasiKPIResponse)
@limiter.limit(LIMIT_READ_DETAIL)
def get_organisasi_kpi(
    request: Request,
    organisasi_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get KPI untuk organisasi tertentu.
    
    ADMIN ONLY atau user dari organisasi itu sendiri.
    
    Limit: 30/menit per IP
    """
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id,
    ).first()
    
    if organisasi is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisasi tidak ditemukan",
        )
    
    # Cek permission: hanya admin atau user dari organisasi itu
    is_admin = _is_admin(current_user)
    is_from_org = current_user.organisasi_id == organisasi_id
    
    if not is_admin and not is_from_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke KPI organisasi ini",
        )
    
    try:
        kpi_data = get_single_organisasi_kpi(db, organisasi_id)
        return schemas.OrganisasiKPIResponse(**kpi_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/all", response_model=schemas.AllOrganisasiKPIResponse)
@limiter.limit(LIMIT_READ_LIST)
def get_all_organisasi_kpi(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get KPI untuk semua organisasi (aktif).
    
    ADMIN ONLY
    
    Limit: 60/menit per IP
    """
    if not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses KPI semua organisasi",
        )
    
    kpi_list = get_all_organisasi_kpi(db)
    
    return schemas.AllOrganisasiKPIResponse(
        kpi_list=[schemas.OrganisasiKPIResponse(**kpi) for kpi in kpi_list]
    )


@router.get("/summary", response_model=dict)
@limiter.limit(LIMIT_READ_LIST)
def get_kpi_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get ringkasan KPI sistem secara keseluruhan (total semua organisasi).
    
    ADMIN ONLY
    
    Limit: 60/menit per IP
    """
    if not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses KPI summary",
        )
    
    all_kpi = get_all_organisasi_kpi(db)
    
    total_organisasi = len(all_kpi)
    total_kegiatan = sum(kpi["total_kegiatan"] for kpi in all_kpi)
    total_completed = sum(kpi["completed"]["count"] for kpi in all_kpi)
    total_delayed = sum(kpi["delayed"]["count"] for kpi in all_kpi)
    total_failed = sum(kpi["failed"]["count"] for kpi in all_kpi)
    total_active = sum(kpi["active"]["count"] for kpi in all_kpi)
    
    if total_kegiatan == 0:
        return {
            "total_organisasi": total_organisasi,
            "total_kegiatan": 0,
            "completed_pct": 0.0,
            "delayed_pct": 0.0,
            "failed_pct": 0.0,
            "active_pct": 0.0,
        }
    
    return {
        "total_organisasi": total_organisasi,
        "total_kegiatan": total_kegiatan,
        "completed_pct": round((total_completed / total_kegiatan) * 100, 2),
        "delayed_pct": round((total_delayed / total_kegiatan) * 100, 2),
        "failed_pct": round((total_failed / total_kegiatan) * 100, 2),
        "active_pct": round((total_active / total_kegiatan) * 100, 2),
        "organisasi_breakdown": all_kpi,
    }
