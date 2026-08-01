from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
<<<<<<< HEAD
=======
from jose import JWTError
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
from sqlalchemy.orm import Session

from app import auth, models
from app.database import get_db

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
<<<<<<< HEAD
    """Dependency to get current authenticated user from JWT token"""
    payload = auth.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kadaluarsa",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
        )
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun Anda tidak aktif",
        )
    
=======
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
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
    return user


def get_current_admin(
    current_user: models.User = Depends(get_current_user),
<<<<<<< HEAD
    db: Session = Depends(get_db),
) -> models.User:
    """Dependency to verify current user is an admin"""
    # Check if user has admin role (role_id == 1)
    admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
    
    if current_user.role_id != admin_role.id if admin_role else False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses admin",
        )
    
=======
) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Butuh role admin"
        )
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
    return current_user
