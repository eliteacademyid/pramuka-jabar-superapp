from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    """Get user by ID or raise 404"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan"
        )
    return user


@router.get("/users", response_model=List[schemas.UserDetailResponse])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """List all users (admin only)"""
    users = (
        db.query(models.User)
        .order_by(models.User.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return users


@router.get("/users/{user_id}", response_model=schemas.UserDetailResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Get specific user (admin only)"""
    user = _get_user_or_404(db, user_id)
    return user


@router.put("/users/{user_id}", response_model=schemas.UserDetailResponse)
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Update user (admin only)"""
    user = _get_user_or_404(db, user_id)

    # Update email if provided
    if payload.email is not None and payload.email != user.email:
        existing = db.query(models.User).filter(models.User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan",
            )
        user.email = payload.email

    # Update full name if provided
    if payload.nama_lengkap is not None:
        user.nama_lengkap = payload.nama_lengkap

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Delete user (admin only)"""
    user = _get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
    return None


@router.get("/roles", response_model=List[schemas.RoleResponse])
def list_roles(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """List all roles (admin only)"""
    roles = db.query(models.Role).order_by(models.Role.id).all()
    return roles


@router.post("/roles", response_model=schemas.RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: schemas.RoleCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Create new role (admin only)"""
    # Check if role already exists
    existing = db.query(models.Role).filter(models.Role.name == role_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role sudah ada",
        )

    new_role = models.Role(**role_data.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role
