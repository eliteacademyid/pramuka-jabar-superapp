from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.get("/{surat_id}", response_model=List[schemas.AuditLogOut])
def get_tracking(
    surat_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    surat = db.query(models.Surat).filter(models.Surat.id == surat_id).first()
    if not surat:
        raise HTTPException(status_code=404, detail="Surat tidak ditemukan")

    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.surat_id == surat_id)
        .order_by(models.AuditLog.created_at.asc())
        .all()
    )

    result = []
    for log in logs:
        data = log.__dict__.copy()
        if log.user_id:
            data["user_info"] = db.query(models.User).filter(models.User.id == log.user_id).first()
        else:
            data["user_info"] = None
        result.append(data)
    return result
