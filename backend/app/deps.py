from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, joinedload

from app import auth, models
from app.database import get_db

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    """Dependency to get the currently authenticated user."""
    payload = auth.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kadaluarsa",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")

    # joinedload role agar get_current_admin tidak perlu query tambahan
    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.id == int(user_id))
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun Anda tidak aktif")

    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Dependency to verify that the current user is an admin."""
    # role sudah di-load oleh get_current_user, tidak perlu query DB lagi
    if not current_user.role or current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anda tidak memiliki akses admin")

    return current_user
