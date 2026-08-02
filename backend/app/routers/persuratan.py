import uuid
from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.config import UPLOAD_DIR
from app.database import get_db
from app.deps import get_current_admin, get_current_user

router = APIRouter(prefix="/admin", tags=["persuratan"])

BULAN_ROMawi = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
    7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}


# ---------- Helper ----------


def _next_urutan(db: Session, jenis: str, tahun: int) -> int:
    """Ambil urutan penomoran berikutnya secara atomik (lock per jenis+tahun).

    Menghindari tabrakan: jika belum ada baris counter, hitung dari jumlah
    data yang sudah ada pada tahun tersebut supaya selaras dengan record lama.
    """
    row = (
        db.query(models.PersuratanCounter)
        .filter_by(jenis=jenis, tahun=tahun)
        .with_for_update()
        .first()
    )
    if not row:
        if jenis == "masuk":
            sudah_ada = (
                db.query(models.SuratMasuk)
                .filter(func.extract("year", models.SuratMasuk.tanggal_diterima) == tahun)
                .count()
            )
        else:
            sudah_ada = (
                db.query(models.SuratKeluar)
                .filter(func.extract("year", models.SuratKeluar.tanggal_surat) == tahun)
                .count()
            )
        row = models.PersuratanCounter(
            jenis=jenis, tahun=tahun, urutan=sudah_ada
        )
        db.add(row)
        db.flush()
    row.urutan += 1
    return row.urutan


def _get_klasifikasi_or_404(db: Session, klasifikasi_id: int) -> models.KlasifikasiSurat:
    obj = (
        db.query(models.KlasifikasiSurat)
        .filter(models.KlasifikasiSurat.id == klasifikasi_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Klasifikasi surat tidak ditemukan")
    return obj


def _get_surat_masuk_or_404(db: Session, sm_id: int) -> models.SuratMasuk:
    obj = (
        db.query(models.SuratMasuk)
        .options(joinedload(models.SuratMasuk.klasifikasi), joinedload(models.SuratMasuk.disposisi))
        .filter(models.SuratMasuk.id == sm_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Surat masuk tidak ditemukan")
    return obj


def _get_surat_keluar_or_404(db: Session, sk_id: int) -> models.SuratKeluar:
    obj = (
        db.query(models.SuratKeluar)
        .options(joinedload(models.SuratKeluar.klasifikasi))
        .filter(models.SuratKeluar.id == sk_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Surat keluar tidak ditemukan")
    return obj


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user


def _cek_sifat(sifat: str):
    if sifat not in models.SIFAT_SURAT:
        raise HTTPException(status_code=400, detail="Sifat surat tidak valid")


def _simpan_file(ext: str, chunk_list: list) -> str:
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    nama_tersimpan = f"{uuid.uuid4().hex}{ext}"
    tujuan = Path(UPLOAD_DIR) / nama_tersimpan
    with open(tujuan, "wb") as out:
        for chunk in chunk_list:
            out.write(chunk)
    return f"/uploads/{nama_tersimpan}"


def _hapus_file(file_url: str):
    if not file_url:
        return
    name = file_url.rsplit("/", 1)[-1]
    path = Path(UPLOAD_DIR) / name
    if path.exists():
        path.unlink()


def _serialize_surat_masuk(db: Session, sm: models.SuratMasuk) -> dict:
    data = schemas.SuratMasukOut.model_validate(sm).model_dump()
    data["nama_klasifikasi"] = sm.klasifikasi.nama_klasifikasi if sm.klasifikasi else ""
    data["nama_diinput"] = sm.diinput_oleh_user.nama_lengkap if sm.diinput_oleh_user else ""
    return data


def _serialize_surat_keluar(db: Session, sk: models.SuratKeluar) -> dict:
    data = schemas.SuratKeluarOut.model_validate(sk).model_dump()
    data["nama_klasifikasi"] = sk.klasifikasi.nama_klasifikasi if sk.klasifikasi else ""
    data["nama_dibuat"] = sk.dibuat_oleh_user.nama_lengkap if sk.dibuat_oleh_user else ""
    return data


def _serialize_disposisi(d: models.Disposisi) -> dict:
    data = schemas.DisposisiOut.model_validate(d).model_dump()
    data["nama_dari"] = d.dari_user.nama_lengkap if d.dari_user else ""
    data["nama_kepada"] = d.kepada_user.nama_lengkap if d.kepada_user else ""
    return data


# ---------- Klasifikasi Surat ----------


@router.get("/klasifikasi-surat", response_model=List[schemas.KlasifikasiSuratOut])
def list_klasifikasi(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    return (
        db.query(models.KlasifikasiSurat)
        .order_by(models.KlasifikasiSurat.kode.asc())
        .all()
    )


@router.post(
    "/klasifikasi-surat",
    response_model=schemas.KlasifikasiSuratOut,
    status_code=status.HTTP_201_CREATED,
)
def create_klasifikasi(
    payload: schemas.KlasifikasiSuratCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if db.query(models.KlasifikasiSurat).filter(
        models.KlasifikasiSurat.kode == payload.kode
    ).first():
        raise HTTPException(status_code=400, detail="Kode klasifikasi sudah ada")
    obj = models.KlasifikasiSurat(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put(
    "/klasifikasi-surat/{klasifikasi_id}",
    response_model=schemas.KlasifikasiSuratOut,
)
def update_klasifikasi(
    klasifikasi_id: int,
    payload: schemas.KlasifikasiSuratUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_klasifikasi_or_404(db, klasifikasi_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("kode"):
        existing = (
            db.query(models.KlasifikasiSurat)
            .filter(models.KlasifikasiSurat.kode == data["kode"])
            .first()
        )
        if existing and existing.id != klasifikasi_id:
            raise HTTPException(status_code=400, detail="Kode klasifikasi sudah ada")
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/klasifikasi-surat/{klasifikasi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_klasifikasi(
    klasifikasi_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_klasifikasi_or_404(db, klasifikasi_id)
    if (
        db.query(models.SuratMasuk)
        .filter(models.SuratMasuk.klasifikasi_id == klasifikasi_id)
        .count()
        or db.query(models.SuratKeluar)
        .filter(models.SuratKeluar.klasifikasi_id == klasifikasi_id)
        .count()
    ):
        raise HTTPException(
            status_code=400,
            detail="Klasifikasi tidak bisa dihapus karena masih dipakai surat",
        )
    db.delete(obj)
    db.commit()


# ---------- Surat Masuk ----------


@router.get("/surat-masuk")
def list_surat_masuk(
    status_: Optional[str] = Query(default=None, alias="status"),
    klasifikasi_id: Optional[int] = Query(default=None),
    sifat: Optional[str] = Query(default=None),
    tanggal_dari: Optional[date] = Query(default=None),
    tanggal_sampai: Optional[date] = Query(default=None),
    q: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.SuratMasuk).options(
        joinedload(models.SuratMasuk.klasifikasi)
    )
    if status_:
        query = query.filter(models.SuratMasuk.status == status_)
    if klasifikasi_id is not None:
        query = query.filter(models.SuratMasuk.klasifikasi_id == klasifikasi_id)
    if sifat:
        query = query.filter(models.SuratMasuk.sifat == sifat)
    if tanggal_dari:
        query = query.filter(models.SuratMasuk.tanggal_diterima >= tanggal_dari)
    if tanggal_sampai:
        query = query.filter(models.SuratMasuk.tanggal_diterima <= tanggal_sampai)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.SuratMasuk.perihal.ilike(like)
            | models.SuratMasuk.pengirim.ilike(like)
            | models.SuratMasuk.nomor_surat_asal.ilike(like)
        )
    total = query.count()
    rows = (
        query.order_by(models.SuratMasuk.tanggal_diterima.desc(), models.SuratMasuk.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "items": [_serialize_surat_masuk(db, sm) for sm in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("/surat-masuk", response_model=schemas.SuratMasukOut, status_code=status.HTTP_201_CREATED)
def create_surat_masuk(
    payload: schemas.SuratMasukCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    _get_klasifikasi_or_404(db, payload.klasifikasi_id)
    _cek_sifat(payload.sifat)
    if payload.tanggal_diterima < payload.tanggal_surat:
        raise HTTPException(
            status_code=400,
            detail="Tanggal diterima tidak boleh sebelum tanggal surat",
        )
    tahun = payload.tanggal_diterima.year
    urutan = _next_urutan(db, "masuk", tahun)
    obj = models.SuratMasuk(
        nomor_agenda=f"AGD/{urutan}/{tahun}",
        nomor_surat_asal=payload.nomor_surat_asal,
        tanggal_surat=payload.tanggal_surat,
        tanggal_diterima=payload.tanggal_diterima,
        pengirim=payload.pengirim,
        perihal=payload.perihal,
        klasifikasi_id=payload.klasifikasi_id,
        sifat=payload.sifat,
        status="baru",
        diinput_oleh=current_admin.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/surat-masuk/{sm_id}")
def get_surat_masuk(
    sm_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    sm = _get_surat_masuk_or_404(db, sm_id)
    data = _serialize_surat_masuk(db, sm)
    data["disposisi"] = [
        _serialize_disposisi(d) for d in sm.disposisi
    ]
    return data


@router.put("/surat-masuk/{sm_id}", response_model=schemas.SuratMasukOut)
def update_surat_masuk(
    sm_id: int,
    payload: schemas.SuratMasukUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_masuk_or_404(db, sm_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("klasifikasi_id"):
        _get_klasifikasi_or_404(db, data["klasifikasi_id"])
    if data.get("sifat"):
        _cek_sifat(data["sifat"])
    if data.get("status") and data["status"] not in models.STATUS_SURAT_MASUK:
        raise HTTPException(status_code=400, detail="Status surat masuk tidak valid")
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/surat-masuk/{sm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_surat_masuk(
    sm_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_masuk_or_404(db, sm_id)
    _hapus_file(obj.file_scan_url)
    db.delete(obj)
    db.commit()


@router.post("/surat-masuk/{sm_id}/scan")
async def upload_scan_surat_masuk(
    sm_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_masuk_or_404(db, sm_id)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in models.SURAT_EXT_IZIN:
        raise HTTPException(
            status_code=400, detail="Tipe file tidak diizinkan (pdf, jpg, png, docx)"
        )
    ukuran = 0
    potongan = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        ukuran += len(chunk)
        potongan.append(chunk)
        if ukuran > models.SURAT_MAX_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400, detail=f"Ukuran file melebihi {models.SURAT_MAX_MB} MB"
            )
    _hapus_file(obj.file_scan_url)
    obj.file_scan_url = _simpan_file(ext, potongan)
    db.commit()
    db.refresh(obj)
    return _serialize_surat_masuk(db, obj)


# ---------- Surat Keluar ----------


@router.get("/surat-keluar")
def list_surat_keluar(
    status_: Optional[str] = Query(default=None, alias="status"),
    klasifikasi_id: Optional[int] = Query(default=None),
    sifat: Optional[str] = Query(default=None),
    tanggal_dari: Optional[date] = Query(default=None),
    tanggal_sampai: Optional[date] = Query(default=None),
    q: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = db.query(models.SuratKeluar).options(
        joinedload(models.SuratKeluar.klasifikasi)
    )
    if status_:
        query = query.filter(models.SuratKeluar.status == status_)
    if klasifikasi_id is not None:
        query = query.filter(models.SuratKeluar.klasifikasi_id == klasifikasi_id)
    if sifat:
        query = query.filter(models.SuratKeluar.sifat == sifat)
    if tanggal_dari:
        query = query.filter(models.SuratKeluar.tanggal_surat >= tanggal_dari)
    if tanggal_sampai:
        query = query.filter(models.SuratKeluar.tanggal_surat <= tanggal_sampai)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.SuratKeluar.perihal.ilike(like)
            | models.SuratKeluar.tujuan.ilike(like)
            | models.SuratKeluar.nomor_surat.ilike(like)
        )
    total = query.count()
    rows = (
        query.order_by(models.SuratKeluar.tanggal_surat.desc(), models.SuratKeluar.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "items": [_serialize_surat_keluar(db, sk) for sk in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post(
    "/surat-keluar",
    response_model=schemas.SuratKeluarOut,
    status_code=status.HTTP_201_CREATED,
)
def create_surat_keluar(
    payload: schemas.SuratKeluarCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    _get_klasifikasi_or_404(db, payload.klasifikasi_id)
    _cek_sifat(payload.sifat)
    obj = models.SuratKeluar(
        nomor_surat=None,
        tanggal_surat=payload.tanggal_surat,
        tujuan=payload.tujuan,
        perihal=payload.perihal,
        klasifikasi_id=payload.klasifikasi_id,
        sifat=payload.sifat,
        isi_ringkas=payload.isi_ringkas,
        status="draft",
        dibuat_oleh=current_admin.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/surat-keluar/{sk_id}")
def get_surat_keluar(
    sk_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    sk = _get_surat_keluar_or_404(db, sk_id)
    return _serialize_surat_keluar(db, sk)


@router.put("/surat-keluar/{sk_id}", response_model=schemas.SuratKeluarOut)
def update_surat_keluar(
    sk_id: int,
    payload: schemas.SuratKeluarUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_keluar_or_404(db, sk_id)
    if obj.status == "terkirim":
        raise HTTPException(
            status_code=400, detail="Surat sudah terkirim, tidak bisa diedit"
        )
    data = payload.model_dump(exclude_unset=True)
    if data.get("klasifikasi_id"):
        _get_klasifikasi_or_404(db, data["klasifikasi_id"])
    if data.get("sifat"):
        _cek_sifat(data["sifat"])
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/surat-keluar/{sk_id}/status", response_model=schemas.SuratKeluarOut)
def update_status_surat_keluar(
    sk_id: int,
    payload: schemas.SuratKeluarStatusUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_keluar_or_404(db, sk_id)
    new_status = payload.status
    if new_status not in models.STATUS_SURAT_KELUAR:
        raise HTTPException(status_code=400, detail="Status surat keluar tidak valid")

    if obj.status == "terkirim":
        raise HTTPException(status_code=400, detail="Surat sudah terkirim, tidak bisa diubah statusnya")

    if new_status == "menunggu_ttd":
        if not obj.nomor_surat:
            tahun = date.today().year
            bulan = BULAN_ROMawi[date.today().month]
            urutan = _next_urutan(db, "keluar", tahun)
            obj.nomor_surat = f"{urutan}/Kwarda-Jabar/{bulan}/{tahun}"
    elif new_status == "terkirim":
        if not obj.file_surat_url:
            raise HTTPException(
                status_code=400,
                detail="File surat wajib diunggah sebelum surat ditandai terkirim",
            )
        if not obj.nomor_surat:
            tahun = date.today().year
            bulan = BULAN_ROMawi[date.today().month]
            urutan = _next_urutan(db, "keluar", tahun)
            obj.nomor_surat = f"{urutan}/Kwarda-Jabar/{bulan}/{tahun}"

    obj.status = new_status
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/surat-keluar/{sk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_surat_keluar(
    sk_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_keluar_or_404(db, sk_id)
    if obj.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Surat keluar hanya bisa dihapus saat masih draft",
        )
    _hapus_file(obj.file_surat_url)
    db.delete(obj)
    db.commit()


@router.post("/surat-keluar/{sk_id}/file")
async def upload_file_surat_keluar(
    sk_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_surat_keluar_or_404(db, sk_id)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in models.SURAT_EXT_IZIN:
        raise HTTPException(
            status_code=400, detail="Tipe file tidak diizinkan (pdf, jpg, png, docx)"
        )
    ukuran = 0
    potongan = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        ukuran += len(chunk)
        potongan.append(chunk)
        if ukuran > models.SURAT_MAX_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400, detail=f"Ukuran file melebihi {models.SURAT_MAX_MB} MB"
            )
    _hapus_file(obj.file_surat_url)
    obj.file_surat_url = _simpan_file(ext, potongan)
    db.commit()
    db.refresh(obj)
    return _serialize_surat_keluar(db, obj)


# ---------- Disposisi ----------


def _get_disposisi_or_404(db: Session, disposisi_id: int) -> models.Disposisi:
    obj = (
        db.query(models.Disposisi)
        .filter(models.Disposisi.id == disposisi_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Disposisi tidak ditemukan")
    return obj


@router.post(
    "/surat-masuk/{sm_id}/disposisi",
    status_code=status.HTTP_201_CREATED,
)
def create_disposisi(
    sm_id: int,
    payload: schemas.DisposisiCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Butuh role admin atau staff",
        )
    sm = _get_surat_masuk_or_404(db, sm_id)
    kepada = _get_user_or_404(db, payload.kepada_user_id)
    if payload.instruksi not in models.INSTRUKSI_DISPOSISI:
        raise HTTPException(status_code=400, detail="Instruksi disposisi tidak valid")
    if payload.kepada_user_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Tidak bisa mendisposisikan kepada diri sendiri"
        )
    if not kepada.is_active:
        raise HTTPException(status_code=400, detail="User tujuan nonaktif")

    obj = models.Disposisi(
        surat_masuk_id=sm.id,
        dari_user_id=current_user.id,
        kepada_user_id=payload.kepada_user_id,
        instruksi=payload.instruksi,
        catatan=payload.catatan,
        status="menunggu",
        tanggal_disposisi=date.today(),
    )
    db.add(obj)
    if sm.status == "baru":
        sm.status = "didisposisikan"
    db.commit()
    db.refresh(obj)
    return _serialize_disposisi(obj)


@router.get("/disposisi/saya")
def list_disposisi_saya(
    status_: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = (
        db.query(models.Disposisi)
        .options(
            joinedload(models.Disposisi.dari_user),
            joinedload(models.Disposisi.kepada_user),
            joinedload(models.Disposisi.surat_masuk),
        )
        .filter(models.Disposisi.kepada_user_id == current_user.id)
    )
    if status_:
        if status_ not in models.STATUS_DISPOSISI:
            raise HTTPException(status_code=400, detail="Status disposisi tidak valid")
        query = query.filter(models.Disposisi.status == status_)
    rows = query.order_by(
        models.Disposisi.status.desc(), models.Disposisi.id.desc()
    ).all()
    result = []
    for d in rows:
        data = _serialize_disposisi(d)
        data["surat"] = {
            "id": d.surat_masuk.id,
            "nomor_agenda": d.surat_masuk.nomor_agenda,
            "perihal": d.surat_masuk.perihal,
            "pengirim": d.surat_masuk.pengirim,
            "tanggal_diterima": d.surat_masuk.tanggal_diterima,
            "sifat": d.surat_masuk.sifat,
            "status_surat": d.surat_masuk.status,
        }
        result.append(data)
    return result


@router.patch("/disposisi/{disposisi_id}/proses")
def proses_disposisi(
    disposisi_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    obj = _get_disposisi_or_404(db, disposisi_id)
    if obj.kepada_user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Hanya penerima disposisi yang bisa memproses"
        )
    if obj.status == "selesai":
        raise HTTPException(status_code=400, detail="Disposisi sudah selesai")
    obj.status = "diproses"
    db.commit()
    db.refresh(obj)
    return _serialize_disposisi(obj)


@router.patch(
    "/disposisi/{disposisi_id}/selesai",
)
def selesaikan_disposisi(
    disposisi_id: int,
    payload: schemas.DisposisiStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    obj = _get_disposisi_or_404(db, disposisi_id)
    if obj.kepada_user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Hanya penerima disposisi yang bisa menandai selesai"
        )
    if not payload.catatan_penyelesaian.strip():
        raise HTTPException(
            status_code=400, detail="Catatan penyelesaian wajib diisi"
        )
    obj.status = "selesai"
    obj.tanggal_selesai = date.today()
    obj.catatan_penyelesaian = payload.catatan_penyelesaian

    semua_selesai = (
        db.query(models.Disposisi)
        .filter(models.Disposisi.surat_masuk_id == obj.surat_masuk_id)
        .all()
    )
    if semua_selesai and all(d.status == "selesai" for d in semua_selesai):
        surat = db.query(models.SuratMasuk).filter(
            models.SuratMasuk.id == obj.surat_masuk_id
        ).first()
        if surat and surat.status != "diarsipkan":
            surat.status = "selesai"

    db.commit()
    db.refresh(obj)
    return _serialize_disposisi(obj)


# ---------- Rekap ----------


@router.get("/persuratan/rekap")
def rekap_persuratan(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    today = date.today()
    bulan_ini = f"{today.year}-{today.month:02d}"

    surat_masuk_bulan_ini = (
        db.query(models.SuratMasuk)
        .filter(models.SuratMasuk.tanggal_diterima >= f"{bulan_ini}-01")
        .filter(models.SuratMasuk.tanggal_diterima < _bulan_berikutnya(bulan_ini))
        .count()
    )
    surat_keluar_bulan_ini = (
        db.query(models.SuratKeluar)
        .filter(models.SuratKeluar.tanggal_surat >= f"{bulan_ini}-01")
        .filter(models.SuratKeluar.tanggal_surat < _bulan_berikutnya(bulan_ini))
        .count()
    )

    disposisi = {}
    for s in models.STATUS_DISPOSISI:
        disposisi[s] = (
            db.query(models.Disposisi).filter(models.Disposisi.status == s).count()
        )
    disposisi_menunggu_saya = (
        db.query(models.Disposisi)
        .filter(
            models.Disposisi.kepada_user_id == current_user.id,
            models.Disposisi.status == "menunggu",
        )
        .count()
    )

    surat_segera_baru = (
        db.query(models.SuratMasuk)
        .filter(
            models.SuratMasuk.sifat == "segera",
            models.SuratMasuk.status == "baru",
        )
        .count()
    )

    total_surat_masuk = db.query(models.SuratMasuk).count()
    total_surat_keluar = db.query(models.SuratKeluar).count()

    return {
        "surat_masuk_bulan_ini": surat_masuk_bulan_ini,
        "surat_keluar_bulan_ini": surat_keluar_bulan_ini,
        "total_surat_masuk": total_surat_masuk,
        "total_surat_keluar": total_surat_keluar,
        "disposisi": disposisi,
        "disposisi_menunggu_saya": disposisi_menunggu_saya,
        "surat_segera_baru": surat_segera_baru,
    }


def _bulan_berikutnya(awal_bulan: str) -> str:
    tahun, bulan = awal_bulan.split("-")
    t = int(tahun)
    b = int(bulan) + 1
    if b > 12:
        b = 1
        t += 1
    return f"{t}-{b:02d}-01"