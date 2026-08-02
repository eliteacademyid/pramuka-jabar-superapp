from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[schemas.NotificationOut])
def list_notifications(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc(), models.Notification.id.desc())
        .limit(30)
        .all()
    )


@router.get("/unread-count")
def unread_count(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = (
        db.query(models.Notification)
        .filter(
            models.Notification.user_id == current_user.id,
            models.Notification.is_read.is_(False),
        )
        .count()
    )
    return {"count": count}


@router.post("/read-all")
def read_all(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read.is_(False),
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}


@router.post("/{notification_id}/read")
def read_one(
    notification_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.get(models.Notification, notification_id)
    if n and n.user_id == current_user.id:
        n.is_read = True
        db.commit()
    return {"ok": True}
