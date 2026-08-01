from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_to_out(user: models.User, role_name: str) -> dict:
    """Serialize User ke dict UserOut tanpa menyentuh relasi lazy."""
    return {
        "id": user.id,
        "username": user.username,
        "nama_lengkap": user.nama_lengkap,
        "role": role_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # EXISTS — tidak fetch semua kolom user hanya untuk cek duplikat
    exists = db.query(
        db.query(models.User).filter(
            (models.User.username == user_data.username) |
            (models.User.email == user_data.username)
        ).exists()
    ).scalar()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username atau email sudah terdaftar",
        )

    # Role lookup — name sudah punya unique index
    role = db.query(models.Role).filter(models.Role.name == "staff").first()
    if not role:
        role = models.Role(name="staff", description="Staff")
        db.add(role)
        db.flush()  # dapat role.id tanpa commit + refresh

    new_user = models.User(
        username=user_data.username,
        email=user_data.username,
        nama_lengkap=user_data.nama_lengkap,
        hashed_password=auth.hash_password(user_data.password),
        role_id=role.id,
    )
    db.add(new_user)
    db.commit()
    # flush memberi id tanpa SELECT ulang — hanya refresh untuk dapat created_at dari DB
    db.refresh(new_user)

    return _user_to_out(new_user, role.name)


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login user and return an access token."""
    # Filter pada kolom username yang sudah punya index
    user = db.query(models.User).filter(
        models.User.username == payload.username
    ).first()

    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun nonaktif",
        )

    token = auth.create_access_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(payload: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh an access token."""
    decoded = auth.verify_token(payload.refresh_token)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kadaluarsa",
        )

    user = db.query(models.User).filter(
        models.User.id == int(decoded.get("sub"))
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan atau tidak aktif",
        )

    token = auth.create_access_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: models.User = Depends(get_current_user)):
    """Client-side logout placeholder."""
    return None


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    """Return current user — role sudah di-joinedload oleh get_current_user."""
    return _user_to_out(
        current_user,
        current_user.role.name if current_user.role else "staff",
    )
