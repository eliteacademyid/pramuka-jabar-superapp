from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, joinedload

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_admin
from app.limiter import limiter, LIMIT_ADMIN_READ, LIMIT_ADMIN_WRITE, LIMIT_DELETE

router = APIRouter(prefix="/admin", tags=["Admin"])


def _serialize_users(users: list) -> List[dict]:
    """Konversi list User ke dict untuk UserOut — hindari akses relasi berkali-kali."""
    return [
        {
            "id": u.id,
            "username": u.username,
            "nama_lengkap": u.nama_lengkap,
            # role sudah di-joinedload, tidak ada query tambahan
            "role": u.role.name if u.role else "staff",
            "is_active": u.is_active,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.get("/users", response_model=List[schemas.UserOut])
@limiter.limit(LIMIT_ADMIN_READ)
def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """List all users (admin only). Limit: 60/menit per IP."""
    query = db.query(models.User).options(
        # joinedload role: satu JOIN query, bukan N lazy-load per user
        joinedload(models.User.role)
    )

    if search:
        query = query.filter(
            models.User.username.ilike(f"%{search}%") |
            models.User.nama_lengkap.ilike(f"%{search}%")
        )

    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)

    users = query.order_by(models.User.id).offset(skip).limit(limit).all()
    return _serialize_users(users)


@router.get("/users/{user_id}", response_model=schemas.UserOut)
@limiter.limit(LIMIT_ADMIN_READ)
def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Get a specific user (admin only). Limit: 60/menit per IP."""
    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")
    return _serialize_users([user])[0]


@router.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMIT_ADMIN_WRITE)
def create_user(
    request: Request,
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Create a new user (admin only). Limit: 20/menit per IP."""
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password minimal 6 karakter")
    if payload.role not in models.ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role tidak valid")

    # EXISTS — tidak fetch semua kolom User
    username_exists = db.query(
        db.query(models.User).filter(models.User.username == payload.username).exists()
    ).scalar()
    if username_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah digunakan")

    # Role lookup — pakai index ix_roles_name (name sudah unique+index di model)
    role = db.query(models.Role).filter(models.Role.name == payload.role).first()
    if not role:
        role = models.Role(name=payload.role, description=f"Role {payload.role}")
        db.add(role)
        db.flush()  # dapat role.id tanpa commit dulu

    user = models.User(
        username=payload.username,
        email=f"{payload.username}@pramuka.local",
        hashed_password=auth.hash_password(payload.password),
        nama_lengkap=payload.nama_lengkap,
        role_id=role.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "nama_lengkap": user.nama_lengkap,
        "role": role.name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.put("/users/{user_id}", response_model=schemas.UserOut)
@limiter.limit(LIMIT_ADMIN_WRITE)
def update_user(
    request: Request,
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    """Update a user (admin only). Limit: 20/menit per IP."""
    # Ambil user sekaligus dengan role (joinedload) — satu query
    user = (
        db.query(models.User)
        .options(joinedload(models.User.role))
        .filter(models.User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    updates: dict = {}

    if payload.username is not None and payload.username != user.username:
        # EXISTS cek duplikat username
        exists = db.query(
            db.query(models.User).filter(models.User.username == payload.username).exists()
        ).scalar()
        if exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah digunakan")
        updates["username"] = payload.username

    if payload.password:
        if len(payload.password) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password minimal 6 karakter")
        updates["hashed_password"] = auth.hash_password(payload.password)

    if payload.nama_lengkap is not None:
        updates["nama_lengkap"] = payload.nama_lengkap

    new_role = user.role  # default role saat ini
    if payload.role is not None:
        if payload.role not in models.ROLES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role tidak valid")
        new_role = db.query(models.Role).filter(models.Role.name == payload.role).first()
        if new_role:
            updates["role_id"] = new_role.id

    if payload.is_active is not None:
        updates["is_active"] = payload.is_active

    if updates:
        db.query(models.User).filter(models.User.id == user_id).update(
            updates, synchronize_session="fetch"
        )
        db.commit()

    return {
        "id": user.id,
        "username": updates.get("username", user.username),
        "nama_lengkap": updates.get("nama_lengkap", user.nama_lengkap),
        "role": new_role.name if new_role else "staff",
        "is_active": updates.get("is_active", user.is_active),
        "created_at": user.created_at,
    }


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(LIMIT_DELETE)
def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    """Delete a user (admin only). Limit: 20/menit per IP."""
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa menghapus akun sendiri",
        )

    # Langsung DELETE — cek rowcount untuk deteksi not found, satu query
    deleted = db.query(models.User).filter(
        models.User.id == user_id
    ).delete(synchronize_session=False)
    db.commit()

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan")

    return None
