"""
Utility functions untuk menangani deadline reminder notifikasi.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app import models


class ReminderType:
    """Tipe reminder deadline."""
    THREE_DAYS = "3_hari_lagi"
    ONE_DAY = "1_hari_lagi"
    OVERDUE = "terlambat"


def calculate_days_until_deadline(deadline: Optional[datetime]) -> Optional[int]:
    """
    Hitung jumlah hari sampai deadline.
    
    Args:
        deadline: Datetime deadline
        
    Returns:
        Jumlah hari (bisa negatif jika sudah lewat), atau None jika deadline tidak ada
    """
    if deadline is None:
        return None
    
    now = datetime.utcnow()
    delta = deadline - now
    return delta.days


def determine_reminder_status(
    deadline: Optional[datetime],
    is_submitted: bool = False,
) -> str:
    """
    Tentukan status reminder berdasarkan deadline dan status laporan.
    
    Args:
        deadline: Datetime deadline
        is_submitted: Apakah laporan sudah submitted
        
    Returns:
        Tipe reminder atau "none" jika tidak ada reminder
    """
    if deadline is None or is_submitted:
        return "none"
    
    days_left = calculate_days_until_deadline(deadline)
    
    if days_left is None:
        return "none"
    
    if days_left < 0:
        return ReminderType.OVERDUE
    elif days_left == 0:
        return ReminderType.ONE_DAY
    elif days_left <= 3:
        return ReminderType.THREE_DAYS
    else:
        return "none"


def should_send_reminder(
    db: Session,
    laporan_id: int,
    user_id: int,
    reminder_type: str,
) -> bool:
    """
    Cek apakah reminder sudah dikirim sebelumnya untuk laporan ini.
    
    Args:
        db: Database session
        laporan_id: ID laporan
        user_id: ID user penerima reminder
        reminder_type: Tipe reminder
        
    Returns:
        True jika reminder belum pernah dikirim, False jika sudah
    """
    existing = db.query(models.DeadlineReminder).filter(
        models.DeadlineReminder.laporan_id == laporan_id,
        models.DeadlineReminder.user_id == user_id,
        models.DeadlineReminder.reminder_type == reminder_type,
    ).first()
    
    return existing is None


def create_or_update_reminder(
    db: Session,
    laporan_id: int,
    user_id: int,
    reminder_type: str,
    is_sent: bool = False,
    sent_at: Optional[datetime] = None,
) -> models.DeadlineReminder:
    """
    Buat atau update reminder deadline.
    
    Args:
        db: Database session
        laporan_id: ID laporan
        user_id: ID user penerima reminder
        reminder_type: Tipe reminder
        is_sent: Apakah reminder sudah dikirim
        sent_at: Waktu reminder dikirim
        
    Returns:
        Model DeadlineReminder yang dibuat atau diupdate
    """
    reminder = db.query(models.DeadlineReminder).filter(
        models.DeadlineReminder.laporan_id == laporan_id,
        models.DeadlineReminder.user_id == user_id,
        models.DeadlineReminder.reminder_type == reminder_type,
    ).first()
    
    if reminder is None:
        reminder = models.DeadlineReminder(
            laporan_id=laporan_id,
            user_id=user_id,
            reminder_type=reminder_type,
            is_sent=is_sent,
            sent_at=sent_at,
        )
        db.add(reminder)
    else:
        reminder.is_sent = is_sent
        reminder.sent_at = sent_at
    
    db.commit()
    db.refresh(reminder)
    return reminder


def mark_reminder_as_sent(
    db: Session,
    reminder_id: int,
) -> models.DeadlineReminder:
    """
    Mark reminder sebagai sudah dikirim.
    
    Args:
        db: Database session
        reminder_id: ID reminder
        
    Returns:
        Model DeadlineReminder yang sudah diupdate
    """
    reminder = db.query(models.DeadlineReminder).filter(
        models.DeadlineReminder.id == reminder_id
    ).first()
    
    if reminder is None:
        raise ValueError(f"Reminder dengan ID {reminder_id} tidak ditemukan")
    
    reminder.is_sent = True
    reminder.sent_at = datetime.utcnow()
    db.commit()
    db.refresh(reminder)
    return reminder


def get_user_deadline_reminders(
    db: Session,
    user_id: int,
    statuses: Optional[List[str]] = None,
) -> List[Tuple[models.Laporan, List[models.DeadlineReminder], str, Optional[int]]]:
    """
    Get semua reminder deadline untuk user, dengan informasi laporan dan status reminder.
    
    Args:
        db: Database session
        user_id: ID user
        statuses: Filter berdasarkan reminder status (optional). 
                  Jika None, return semua reminders.
                  
    Returns:
        List of tuples: (Laporan, List[DeadlineReminder], reminder_status, days_until_deadline)
    """
    # Get semua laporan milik user yang belum submitted dan punya deadline
    laporans = db.query(models.Laporan).filter(
        models.Laporan.created_by_id == user_id,
        models.Laporan.deadline.isnot(None),
    ).all()
    
    results = []
    
    for laporan in laporans:
        is_submitted = laporan.status == "submitted"
        reminder_status = determine_reminder_status(laporan.deadline, is_submitted)
        
        # Filter berdasarkan statuses jika disediakan
        if statuses and reminder_status not in statuses:
            continue
        
        # Get reminders untuk laporan ini
        reminders = db.query(models.DeadlineReminder).filter(
            models.DeadlineReminder.laporan_id == laporan.id,
        ).all()
        
        days_left = calculate_days_until_deadline(laporan.deadline)
        
        results.append((laporan, reminders, reminder_status, days_left))
    
    return results


def get_pending_reminders_to_send(
    db: Session,
) -> List[Tuple[models.Laporan, models.User, str]]:
    """
    Get semua reminder yang belum dikirim dan perlu dikirim.
    
    Returns:
        List of tuples: (Laporan, User, reminder_type)
    """
    # Get semua laporan dengan deadline yang belum submitted
    laporans = db.query(models.Laporan).filter(
        models.Laporan.deadline.isnot(None),
        models.Laporan.status != "submitted",
    ).all()
    
    pending_reminders = []
    
    for laporan in laporans:
        reminder_status = determine_reminder_status(laporan.deadline, False)
        
        if reminder_status == "none":
            continue
        
        # Get user pemilik laporan
        user = laporan.creator
        if user is None:
            continue
        
        # Cek apakah reminder sudah dikirim
        if should_send_reminder(db, laporan.id, user.id, reminder_status):
            pending_reminders.append((laporan, user, reminder_status))
    
    return pending_reminders
