from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_user
from app.services.common import ensure_wallet

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username sudah terdaftar",
        )

    user = models.User(
        username=payload.username,
        hashed_password=auth.hash_password(payload.password),
        nama_lengkap=payload.nama_lengkap,
        email=payload.email,
        account_type=payload.account_type,
        scout_number=payload.scout_number,
        kwartir=payload.kwartir,
        golongan=payload.golongan,
        role="member",
        is_active=True,
    )
    db.add(user)
    db.flush()
    ensure_wallet(db, user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .first()
    )
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Akun nonaktif"
        )
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.MeOut)
def me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    wallet = (
        db.query(models.Wallet).filter(models.Wallet.user_id == current_user.id).first()
    )
    store = (
        db.query(models.Store)
        .filter(models.Store.owner_id == current_user.id)
        .order_by(models.Store.id.desc())
        .first()
    )
    return {
        "user": current_user,
        "wallet": wallet,
        "store": store,
    }
