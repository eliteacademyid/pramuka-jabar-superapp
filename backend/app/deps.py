from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app import auth, models
from app.database import get_db

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload = auth.decode_access_token(credentials.credentials)
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau kedaluwarsa",
        )

    user = (
        db.query(models.User).filter(models.User.username == username).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User tidak ditemukan"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Akun nonaktif"
        )
    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Butuh role admin"
        )
    return current_user


def require_staff_or_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Butuh role staff atau admin",
        )
    return current_user


def get_active_store(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> models.Store:
    store = (
        db.query(models.Store)
        .filter(
            models.Store.owner_id == current_user.id,
            models.Store.status == "active",
        )
        .first()
    )
    if not store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anda belum memiliki toko aktif",
        )
    return store


def get_store_owner(
    store: models.Store = Depends(get_active_store),
    current_user: models.User = Depends(get_current_user),
) -> models.Store:
    if store.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses",
        )
    return store
