from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_admin, get_current_pembina_or_admin, get_current_super_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan"
        )
    return user


@router.get("/users", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return db.query(models.User).order_by(models.User.id).all()


@router.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password minimal 6 karakter",
        )
    existing = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah digunakan",
        )

    user = models.User(
        username=payload.username,
        hashed_password=auth.hash_password(payload.password),
        nama_lengkap=payload.nama_lengkap,
        role=payload.role,
        is_active=True,
        wilayah_scope_id=payload.wilayah_scope_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    user = _get_user_or_404(db, user_id)

    if payload.username is not None and payload.username != user.username:
        existing = (
            db.query(models.User)
            .filter(models.User.username == payload.username)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah digunakan",
            )
        user.username = payload.username

    if payload.password:
        if len(payload.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password minimal 6 karakter",
            )
        user.hashed_password = auth.hash_password(payload.password)

    if payload.nama_lengkap is not None:
        user.nama_lengkap = payload.nama_lengkap

    if payload.role is not None:
        user.role = payload.role

    if payload.wilayah_scope_id is not None:
        user.wilayah_scope_id = payload.wilayah_scope_id

    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa menghapus akun sendiri",
        )
    user = _get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
