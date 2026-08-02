"""
Utility functions untuk menghitung KPI (Key Performance Indicators) organisasi.

KPI yang dihitung:
- Program selesai (completed): Kegiatan dengan status "completed" dan tanggal_selesai <= hari ini
- Program terlambat (delayed): Kegiatan dengan status "active" namun tanggal_selesai < hari ini
- Program gagal (failed): Kegiatan dengan status "cancelled" atau "failed"
- Program aktif (active): Kegiatan dengan status "active" dan tanggal_selesai >= hari ini
"""

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app import models


class KPIStatus:
    """Status kegiatan untuk KPI calculation."""
    COMPLETED = "completed"
    DELAYED = "delayed"
    FAILED = "failed"
    ACTIVE = "active"


def determine_kegiatan_kpi_status(kegiatan: models.Kegiatan) -> str:
    """
    Tentukan KPI status dari satu kegiatan.
    
    Logic:
    1. Jika status = "completed" → COMPLETED
    2. Jika status = "cancelled" atau "failed" → FAILED
    3. Jika status = "active":
       - Jika tanggal_selesai < hari ini → DELAYED
       - Jika tanggal_selesai >= hari ini → ACTIVE
    4. Else → ACTIVE (default)
    
    Args:
        kegiatan: Model Kegiatan
        
    Returns:
        KPI status string
    """
    if kegiatan.status == "completed":
        return KPIStatus.COMPLETED
    
    if kegiatan.status in ("cancelled", "failed"):
        return KPIStatus.FAILED
    
    if kegiatan.status == "active":
        if kegiatan.tanggal_selesai is None:
            return KPIStatus.ACTIVE
        
        now = datetime.utcnow()
        if kegiatan.tanggal_selesai < now:
            return KPIStatus.DELAYED
        else:
            return KPIStatus.ACTIVE
    
    return KPIStatus.ACTIVE


def calculate_organisasi_kpi(
    db: Session,
    organisasi_id: int,
) -> Tuple[int, int, int, int, int]:
    """
    Hitung KPI untuk satu organisasi.
    
    Args:
        db: Database session
        organisasi_id: ID organisasi
        
    Returns:
        Tuple: (total, completed_count, delayed_count, failed_count, active_count)
    """
    # Get semua kegiatan dari programs yang terhubung ke organisasi
    kegiatans = db.query(models.Kegiatan).join(
        models.Program,
        models.Kegiatan.program_id == models.Program.id,
    ).filter(
        models.Program.organisasi_id == organisasi_id,
    ).all()
    
    total = len(kegiatans)
    
    if total == 0:
        return 0, 0, 0, 0, 0
    
    completed_count = 0
    delayed_count = 0
    failed_count = 0
    active_count = 0
    
    for kegiatan in kegiatans:
        kpi_status = determine_kegiatan_kpi_status(kegiatan)
        
        if kpi_status == KPIStatus.COMPLETED:
            completed_count += 1
        elif kpi_status == KPIStatus.DELAYED:
            delayed_count += 1
        elif kpi_status == KPIStatus.FAILED:
            failed_count += 1
        elif kpi_status == KPIStatus.ACTIVE:
            active_count += 1
    
    return total, completed_count, delayed_count, failed_count, active_count


def calculate_percentage(count: int, total: int) -> float:
    """
    Hitung persentase dari count terhadap total.
    
    Args:
        count: Jumlah item
        total: Total item
        
    Returns:
        Persentase (0-100), atau 0.0 jika total = 0
    """
    if total == 0:
        return 0.0
    return round((count / total) * 100, 2)


def get_single_organisasi_kpi(
    db: Session,
    organisasi_id: int,
) -> dict:
    """
    Get KPI untuk satu organisasi dengan format response.
    
    Args:
        db: Database session
        organisasi_id: ID organisasi
        
    Returns:
        Dictionary dengan KPI data
    """
    organisasi = db.query(models.Organisasi).filter(
        models.Organisasi.id == organisasi_id,
    ).first()
    
    if organisasi is None:
        raise ValueError(f"Organisasi dengan ID {organisasi_id} tidak ditemukan")
    
    total, completed, delayed, failed, active = calculate_organisasi_kpi(db, organisasi_id)
    
    return {
        "organisasi_id": organisasi.id,
        "organisasi_nama": organisasi.nama,
        "total_kegiatan": total,
        "completed": {
            "label": "Program selesai",
            "value": calculate_percentage(completed, total),
            "count": completed,
        },
        "delayed": {
            "label": "Program terlambat",
            "value": calculate_percentage(delayed, total),
            "count": delayed,
        },
        "failed": {
            "label": "Program gagal",
            "value": calculate_percentage(failed, total),
            "count": failed,
        },
        "active": {
            "label": "Program aktif",
            "value": calculate_percentage(active, total),
            "count": active,
        },
        "last_updated": datetime.utcnow(),
    }


def get_all_organisasi_kpi(db: Session) -> List[dict]:
    """
    Get KPI untuk semua organisasi.
    
    Args:
        db: Database session
        
    Returns:
        List of KPI data untuk setiap organisasi
    """
    organisasis = db.query(models.Organisasi).filter(
        models.Organisasi.is_active == True,
    ).all()
    
    kpi_list = []
    for organisasi in organisasis:
        try:
            kpi_data = get_single_organisasi_kpi(db, organisasi.id)
            kpi_list.append(kpi_data)
        except Exception as e:
            print(f"Error calculating KPI for organisasi {organisasi.id}: {e}")
            continue
    
    return kpi_list


def get_organisasi_kpi_by_user(
    db: Session,
    user_id: int,
) -> Optional[dict]:
    """
    Get KPI untuk organisasi yang terkait dengan user.
    
    Args:
        db: Database session
        user_id: ID user
        
    Returns:
        KPI data atau None jika user tidak ada organisasi
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None or user.organisasi_id is None:
        return None
    
    return get_single_organisasi_kpi(db, user.organisasi_id)
