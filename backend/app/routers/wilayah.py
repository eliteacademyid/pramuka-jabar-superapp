from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin

router = APIRouter(prefix="/admin", tags=["wilayah"])


def _get_kwarcab_or_404(db: Session, kwarcab_id: int) -> models.Kwarcab:
    obj = db.query(models.Kwarcab).filter(models.Kwarcab.id == kwarcab_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kwarcab tidak ditemukan"
        )
    return obj


def _get_kwaran_or_404(db: Session, kwaran_id: int) -> models.Kwaran:
    obj = db.query(models.Kwaran).filter(models.Kwaran.id == kwaran_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kwaran tidak ditemukan"
        )
    return obj


def _get_gudep_or_404(db: Session, gudep_id: int) -> models.Gudep:
    obj = db.query(models.Gudep).filter(models.Gudep.id == gudep_id).first()
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gudep tidak ditemukan"
        )
    return obj


# ---------- Kwarcab ----------


@router.get("/kwarcab", response_model=List[schemas.KwarcabOut])
def list_kwarcab(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return db.query(models.Kwarcab).order_by(models.Kwarcab.nama).all()


@router.post("/kwarcab", response_model=schemas.KwarcabOut, status_code=status.HTTP_201_CREATED)
def create_kwarcab(
    payload: schemas.KwarcabCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if (
        db.query(models.Kwarcab)
        .filter(models.Kwarcab.kode_wilayah == payload.kode_wilayah)
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode wilayah sudah digunakan",
        )
    obj = models.Kwarcab(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/kwarcab/{kwarcab_id}", response_model=schemas.KwarcabOut)
def update_kwarcab(
    kwarcab_id: int,
    payload: schemas.KwarcabUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kwarcab_or_404(db, kwarcab_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("kode_wilayah") and data["kode_wilayah"] != obj.kode_wilayah:
        if (
            db.query(models.Kwarcab)
            .filter(models.Kwarcab.kode_wilayah == data["kode_wilayah"])
            .first()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kode wilayah sudah digunakan",
            )
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/kwarcab/{kwarcab_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kwarcab(
    kwarcab_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kwarcab_or_404(db, kwarcab_id)
    if db.query(models.Kwaran).filter(models.Kwaran.kwarcab_id == kwarcab_id).count():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa dihapus: masih ada kwaran di bawah kwarcab ini",
        )
    db.delete(obj)
    db.commit()


# ---------- Kwaran ----------


@router.get("/kwaran")
def list_kwaran(
    kwarcab_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.Kwaran).options(joinedload(models.Kwaran.kwarcab))
    if kwarcab_id is not None:
        query = query.filter(models.Kwaran.kwarcab_id == kwarcab_id)
    rows = query.order_by(models.Kwaran.nama).all()
    return [
        {
            **schemas.KwaranOut.model_validate(k).model_dump(),
            "kwarcab_nama": k.kwarcab.nama if k.kwarcab else "",
        }
        for k in rows
    ]


@router.post("/kwaran", response_model=schemas.KwaranOut, status_code=status.HTTP_201_CREATED)
def create_kwaran(
    payload: schemas.KwaranCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_kwarcab_or_404(db, payload.kwarcab_id)
    obj = models.Kwaran(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/kwaran/{kwaran_id}", response_model=schemas.KwaranOut)
def update_kwaran(
    kwaran_id: int,
    payload: schemas.KwaranUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kwaran_or_404(db, kwaran_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("kwarcab_id"):
        _get_kwarcab_or_404(db, data["kwarcab_id"])
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/kwaran/{kwaran_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_kwaran(
    kwaran_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kwaran_or_404(db, kwaran_id)
    if db.query(models.Gudep).filter(models.Gudep.kwaran_id == kwaran_id).count():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa dihapus: masih ada gudep di bawah kwaran ini",
        )
    db.delete(obj)
    db.commit()


# ---------- Gudep ----------


@router.get("/gudep")
def list_gudep(
    kwaran_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.Gudep).options(joinedload(models.Gudep.kwaran))
    if kwaran_id is not None:
        query = query.filter(models.Gudep.kwaran_id == kwaran_id)
    rows = query.order_by(models.Gudep.nama_pangkalan).all()
    return [
        {
            **schemas.GudepOut.model_validate(g).model_dump(),
            "kwaran_nama": g.kwaran.nama if g.kwaran else "",
        }
        for g in rows
    ]


@router.post("/gudep", response_model=schemas.GudepOut, status_code=status.HTTP_201_CREATED)
def create_gudep(
    payload: schemas.GudepCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_kwaran_or_404(db, payload.kwaran_id)
    obj = models.Gudep(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/gudep/{gudep_id}", response_model=schemas.GudepOut)
def update_gudep(
    gudep_id: int,
    payload: schemas.GudepUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_gudep_or_404(db, gudep_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("kwaran_id"):
        _get_kwaran_or_404(db, data["kwaran_id"])
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/gudep/{gudep_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gudep(
    gudep_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_gudep_or_404(db, gudep_id)
    if db.query(models.Anggota).filter(models.Anggota.gudep_id == gudep_id).count():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak bisa dihapus: masih ada anggota di gudep ini",
        )
    db.delete(obj)
    db.commit()
