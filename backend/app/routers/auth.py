from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import auth, models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.get("/me")
def me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = schemas.UserOut.model_validate(current_user).model_dump()
    if current_user.tingkat_wilayah and current_user.wilayah_id:
        from app.hub_utils import nama_wilayah

        data["nama_wilayah"] = nama_wilayah(
            db, current_user.tingkat_wilayah, current_user.wilayah_id
        )
    else:
        data["nama_wilayah"] = ""
    return data
