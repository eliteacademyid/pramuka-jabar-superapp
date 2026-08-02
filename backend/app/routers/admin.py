from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User tidak ditemukan"
        )
    return user


def _validasi_wilayah_kontributor(db, role, tingkat, wilayah_id):
    if role == "kontributor":
        if not tingkat or not wilayah_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kontributor wajib mengisi tingkat wilayah dan wilayah",
            )
        if tingkat not in models.TINGKAT_WILAYAH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tingkat wilayah tidak valid",
            )
        tabel = {
            "kwarcab": models.Kwarcab,
            "kwaran": models.Kwaran,
            "gudep": models.Gudep,
        }[tingkat]
        if not db.query(tabel).filter(tabel.id == wilayah_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wilayah tidak ditemukan",
            )


def _validasi_anggota_penjual(db, role, anggota_id):
    if role == "penjual" and anggota_id is not None:
        if not db.query(models.Anggota).filter(models.Anggota.id == anggota_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anggota tidak ditemukan",
            )


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
    if payload.role not in models.ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Role tidak valid"
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

    _validasi_wilayah_kontributor(
        db, payload.role, payload.tingkat_wilayah, payload.wilayah_id
    )
    _validasi_anggota_penjual(db, payload.role, payload.anggota_id)
    if payload.role != "kontributor":
        tingkat, wilayah = None, None
    else:
        tingkat, wilayah = payload.tingkat_wilayah, payload.wilayah_id

    user = models.User(
        username=payload.username,
        hashed_password=auth.hash_password(payload.password),
        nama_lengkap=payload.nama_lengkap,
        role=payload.role,
        tingkat_wilayah=tingkat,
        wilayah_id=wilayah,
        anggota_id=payload.anggota_id,
        is_active=True,
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
        if payload.role not in models.ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role tidak valid"
            )
        _validasi_anggota_penjual(db, payload.role, payload.anggota_id)
        user.role = payload.role

    if payload.role is not None and payload.role == "kontributor":
        tingkat = (
            payload.tingkat_wilayah
            if payload.tingkat_wilayah is not None
            else user.tingkat_wilayah
        )
        wilayah = payload.wilayah_id if payload.wilayah_id is not None else user.wilayah_id
        _validasi_wilayah_kontributor(db, "kontributor", tingkat, wilayah)
        user.tingkat_wilayah = tingkat
        user.wilayah_id = wilayah
    elif payload.role is not None and payload.role != "kontributor":
        user.tingkat_wilayah = None
        user.wilayah_id = None

    if payload.anggota_id is not None:
        _validasi_anggota_penjual(db, "penjual", payload.anggota_id)
        user.anggota_id = payload.anggota_id

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
