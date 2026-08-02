from sqlalchemy.orm import Session

from app import models


def notify(
    db: Session,
    user_id: int,
    ntype: str,
    title: str,
    body: str | None = None,
    link: str | None = None,
) -> models.Notification:
    """Buat notifikasi in-app untuk user (ntype: order / chat / wallet)."""
    n = models.Notification(
        user_id=user_id,
        ntype=ntype,
        title=title,
        body=body,
        link=link,
    )
    db.add(n)
    db.flush()
    return n
