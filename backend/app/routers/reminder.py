"""
Router untuk Deadline Reminder - notifikasi deadline laporan.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db  
from app.deps import get_current_user
from app.limiter import limiter, LIMIT_READ_LIST, LIMIT_READ_DETAIL
from app.utils.deadline_reminder import (
    get_user_deadline_reminders,
    get_pending_reminders_to_send,
    determine_reminder_status,
    calculate_days_until_deadline,
)

router = APIRouter(prefix="/reminders", tags=["Deadline Reminders"])


def _is_admin(user: models.User) -> bool:
    """Cek admin via nama role."""
    return user.role is not None and user.role.name == "admin"


@router.get("/my-deadlines", response_model=List[schemas.UserDeadlineRemindersResponse])
@limiter.limit(LIMIT_READ_LIST)
def get_my_deadline_reminders(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    status_filter: Optional[str] = Query(
        None,
        description="Filter berdasarkan reminder status: 3_hari_lagi, 1_hari_lagi, terlambat, none",
    ),
):
    """
    Get semua deadline reminders untuk user yang login.
    
    Mengembalikan laporan dengan deadline yang tertampil di dashboard dengan status reminder,
    contoh: laporan dengan deadline 3 hari lagi, 1 hari lagi, atau terlambat.
    
    Limit: 60/menit per IP
    """
    statuses = [status_filter] if status_filter else None
    reminders_data = get_user_deadline_reminders(db, current_user.id, statuses)
    
    result = []
    for laporan, reminders, reminder_status, days_left in reminders_data:
        result.append(
            schemas.UserDeadlineRemindersResponse(
                laporan=schemas.LaporanResponse.model_validate(laporan),
                reminders=[
                    schemas.DeadlineReminderResponse.model_validate(r) for r in reminders
                ],
                reminder_status=reminder_status,
                days_until_deadline=days_left,
            )
        )
    
    return result


@router.get("/pending", response_model=List[dict])
@limiter.limit(LIMIT_READ_DETAIL)
def get_pending_reminders(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get semua reminder yang belum dikirim dan perlu dikirim.
    
    ADMIN ONLY - untuk monitoring dan debugging reminder system.
    
    Limit: 30/menit per IP
    """
    if not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses pending reminders",
        )
    
    pending = get_pending_reminders_to_send(db)
    
    result = []
    for laporan, user, reminder_type in pending:
        result.append({
            "laporan_id": laporan.id,
            "laporan_judul": laporan.judul,
            "user_id": user.id,
            "user_nama": user.nama_lengkap,
            "deadline": laporan.deadline,
            "reminder_type": reminder_type,
            "days_until_deadline": calculate_days_until_deadline(laporan.deadline),
        })
    
    return result


@router.post("/my-deadlines/{laporan_id}/acknowledge", status_code=status.HTTP_200_OK)
@limiter.limit(LIMIT_READ_LIST)
def acknowledge_deadline_reminder(
    request: Request,
    laporan_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Acknowledge (tandai baca) reminder deadline.
    
    Ini untuk membantu user track reminder mana yang sudah dilihat.
    """
    laporan = db.query(models.Laporan).filter(
        models.Laporan.id == laporan_id,
        models.Laporan.created_by_id == current_user.id,
    ).first()
    
    if laporan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Laporan tidak ditemukan",
        )
    
    if laporan.deadline is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Laporan tidak memiliki deadline",
        )
    
    # Hanya bisa acknowledge jika status laporan masih draft
    if laporan.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hanya laporan dengan status draft yang bisa di-acknowledge",
        )
    
    return {
        "message": "Reminder acknowledged",
        "laporan_id": laporan_id,
        "status": determine_reminder_status(laporan.deadline, False),
        "days_until_deadline": calculate_days_until_deadline(laporan.deadline),
    }
