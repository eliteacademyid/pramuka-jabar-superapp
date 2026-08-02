from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app import auth, models
from app.database import get_db

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload = auth.decode_access_token(credentials.credentials)
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid"
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


def get_current_kontributor(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != "kontributor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Butuh role kontributor"
        )
    if not current_user.tingkat_wilayah or not current_user.wilayah_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun kontributor belum terhubung ke wilayah",
        )
    return current_user


def get_current_penjual(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role != "penjual":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Butuh role penjual"
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    """Kembalikan user jika token valid dikirim, jika tidak kembalikan None.

    Dipakai endpoint publik seperti checkout supaya pembeli yang login bisa
    tercatat (pembeli_user_id), sementara tamu tetap boleh checkout.
    """
    if not credentials:
        return None
    try:
        payload = auth.decode_access_token(credentials.credentials)
    except JWTError:
        return None
    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user or not user.is_active:
        return None
    return user
