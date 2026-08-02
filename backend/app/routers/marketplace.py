import uuid
from datetime import date
from pathlib import Path
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
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
from app.deps import get_current_admin, get_current_penjual, get_optional_user

publik_router = APIRouter(prefix="/public/marketplace", tags=["marketplace-publik"])
penjual_router = APIRouter(prefix="/penjual", tags=["marketplace-penjual"])
admin_router = APIRouter(prefix="/admin/marketplace", tags=["marketplace-admin"])


# ---------- Helper bersama ----------


def _simpan_file(ext: str, chunk_list: list) -> str:
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    nama_tersimpan = f"{uuid.uuid4().hex}{ext}"
    tujuan = Path(UPLOAD_DIR) / nama_tersimpan
    with open(tujuan, "wb") as out:
        for chunk in chunk_list:
            out.write(chunk)
    return f"/uploads/{nama_tersimpan}"


def _hapus_file(file_url: Optional[str]):
    if not file_url:
        return
    name = file_url.rsplit("/", 1)[-1]
    path = Path(UPLOAD_DIR) / name
    if path.exists():
        path.unlink()


async def _baca_file(
    file: UploadFile,
    ext_izin: tuple,
    max_mb: int,
    jenis: str,
) -> tuple:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ext_izin:
        izin_str = ", ".join(ext_izin)
        raise HTTPException(
            status_code=400,
            detail=f"Tipe file {jenis} tidak diizinkan ({izin_str})",
        )
    ukuran = 0
    potongan = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        ukuran += len(chunk)
        potongan.append(chunk)
        if ukuran > max_mb * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Ukuran file {jenis} melebihi {max_mb} MB",
            )
    if not potongan:
        raise HTTPException(status_code=400, detail=f"File {jenis} kosong")
    return ext, potongan


def _serialize_toko(db: Session, toko: models.Toko) -> dict:
    data = schemas.TokoOut.model_validate(toko).model_dump()
    data["nama_pemilik"] = toko.user.nama_lengkap if toko.user else ""
    data["jumlah_produk"] = sum(
        1 for p in toko.produk if p.status == "aktif"
    ) if toko.produk else 0
    return data


def _serialize_produk(db: Session, produk: models.Produk) -> dict:
    data = schemas.ProdukOut.model_validate(produk).model_dump()
    data["nama_toko"] = produk.toko.nama_toko if produk.toko else ""
    data["nama_pemilik_toko"] = (
        produk.toko.user.nama_lengkap if produk.toko and produk.toko.user else ""
    )
    data["nama_kategori"] = produk.kategori.nama_kategori if produk.kategori else ""
    return data


def _serialize_toko_publik(db: Session, toko: models.Toko) -> dict:
    """Serialisasi toko HANYA untuk endpoint publik.

    Tidak membocorkan rekening (nomor/bank/pemilik rekening), WhatsApp, maupun
    identitas pribadi pemilik toko.
    """
    return {
        "id": toko.id,
        "nama_toko": toko.nama_toko,
        "deskripsi": toko.deskripsi,
        "logo_url": toko.logo_url,
        "status": toko.status,
        "jumlah_produk": sum(
            1 for p in toko.produk if p.status == "aktif"
        ) if toko.produk else 0,
    }


def _serialize_produk_publik(db: Session, produk: models.Produk) -> dict:
    """Serialisasi produk HANYA untuk endpoint publik (tanpa identitas pemilik)."""
    return {
        "id": produk.id,
        "toko_id": produk.toko_id,
        "kategori_id": produk.kategori_id,
        "nama_produk": produk.nama_produk,
        "deskripsi": produk.deskripsi,
        "harga": produk.harga,
        "stok": produk.stok,
        "foto_url": produk.foto_url,
        "status": produk.status,
        "nama_toko": produk.toko.nama_toko if produk.toko else "",
        "nama_kategori": produk.kategori.nama_kategori if produk.kategori else "",
    }


def _serialize_pesanan(db: Session, pesanan: models.Pesanan) -> dict:
    data = {
        "id": pesanan.id,
        "nomor_pesanan": pesanan.nomor_pesanan,
        "pembeli_user_id": pesanan.pembeli_user_id,
        "toko_id": pesanan.toko_id,
        "nama_toko": pesanan.toko.nama_toko if pesanan.toko else "",
        "nama_pemilik_toko": (
            pesanan.toko.user.nama_lengkap if pesanan.toko and pesanan.toko.user else ""
        ),
        "nama_pembeli": pesanan.nama_pembeli,
        "kontak_pembeli": pesanan.kontak_pembeli,
        "alamat_pengiriman": pesanan.alamat_pengiriman,
        "total_harga": pesanan.total_harga,
        "status": pesanan.status,
        "bukti_transfer_url": pesanan.bukti_transfer_url,
        "catatan_pembeli": pesanan.catatan_pembeli,
        "created_at": pesanan.created_at,
        "updated_at": pesanan.updated_at,
        "rekening": {
            "nama_bank": pesanan.toko.nama_bank if pesanan.toko else "",
            "nomor_rekening": pesanan.toko.nomor_rekening if pesanan.toko else "",
            "nama_pemilik_rekening": (
                pesanan.toko.nama_pemilik_rekening if pesanan.toko else ""
            ),
            "nomor_wa": pesanan.toko.nomor_wa if pesanan.toko else None,
        },
        "items": [
            {
                "id": item.id,
                "produk_id": item.produk_id,
                "nama_produk_saat_beli": item.nama_produk_saat_beli,
                "harga_saat_beli": item.harga_saat_beli,
                "jumlah": item.jumlah,
                "subtotal": item.subtotal,
            }
            for item in pesanan.items
        ],
    }
    return data


def _get_toko_by_user(db: Session, user_id: int) -> Optional[models.Toko]:
    return db.query(models.Toko).filter(models.Toko.user_id == user_id).first()


def _next_urutan_pesanan(db: Session, tahun: int, bulan: int) -> int:
    """Ambil urutan penomoran pesanan berikutnya secara atomik per tahun+bulan."""
    row = (
        db.query(models.PesananCounter)
        .filter_by(tahun=tahun, bulan=bulan)
        .with_for_update()
        .first()
    )
    if not row:
        sudah_ada = (
            db.query(models.Pesanan)
            .filter(
                func.extract("year", models.Pesanan.created_at) == tahun,
                func.extract("month", models.Pesanan.created_at) == bulan,
            )
            .count()
        )
        row = models.PesananCounter(
            tahun=tahun, bulan=bulan, urutan=sudah_ada
        )
        db.add(row)
        db.flush()
    row.urutan += 1
    return row.urutan


def _buat_nomor_pesanan(db: Session) -> str:
    hari_ini = date.today()
    urutan = _next_urutan_pesanan(db, hari_ini.year, hari_ini.month)
    return f"ORD-{hari_ini.year}{hari_ini.month:02d}-{urutan:03d}"


def _get_pesanan_owned(
    db: Session, pesanan_id: int, toko_id: int
) -> models.Pesanan:
    obj = (
        db.query(models.Pesanan)
        .options(
            joinedload(models.Pesanan.toko).joinedload(models.Toko.user),
            joinedload(models.Pesanan.items),
        )
        .filter(models.Pesanan.id == pesanan_id, models.Pesanan.toko_id == toko_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Pesanan tidak ditemukan")
    return obj


def _get_kategori_or_404(db: Session, kategori_id: int) -> models.KategoriProduk:
    obj = (
        db.query(models.KategoriProduk)
        .filter(models.KategoriProduk.id == kategori_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Kategori produk tidak ditemukan")
    return obj


# =====================================================================
# Endpoint Publik (tanpa auth)
# =====================================================================


@publik_router.get("/produk")
def list_produk_publik(
    kategori_id: Optional[int] = Query(default=None),
    toko_id: Optional[int] = Query(default=None),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Produk)
        .options(
            joinedload(models.Produk.toko).joinedload(models.Toko.user),
            joinedload(models.Produk.kategori),
        )
        .join(models.Toko, models.Toko.id == models.Produk.toko_id)
        .filter(models.Produk.status == "aktif", models.Toko.status == "aktif")
    )
    if kategori_id is not None:
        query = query.filter(models.Produk.kategori_id == kategori_id)
    if toko_id is not None:
        query = query.filter(models.Produk.toko_id == toko_id)
    if search:
        query = query.filter(models.Produk.nama_produk.ilike(f"%{search}%"))

    total = query.count()
    items = (
        query.order_by(models.Produk.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "items": [_serialize_produk_publik(db, p) for p in items],
    }


@publik_router.get("/produk/{produk_id}")
def get_produk_publik(produk_id: int, db: Session = Depends(get_db)):
    produk = (
        db.query(models.Produk)
        .options(
            joinedload(models.Produk.toko).joinedload(models.Toko.user),
            joinedload(models.Produk.kategori),
        )
        .filter(
            models.Produk.id == produk_id,
            models.Produk.status == "aktif",
            models.Produk.toko.has(status="aktif"),
        )
        .first()
    )
    if not produk:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return _serialize_produk_publik(db, produk)


@publik_router.get("/toko")
def list_toko_publik(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Toko)
        .options(
            joinedload(models.Toko.user),
            joinedload(models.Toko.produk),
        )
        .filter(models.Toko.status == "aktif")
        .order_by(models.Toko.nama_toko.asc())
        .all()
    )
    return [_serialize_toko_publik(db, t) for t in rows]


@publik_router.get("/toko/{toko_id}")
def get_toko_publik(toko_id: int, db: Session = Depends(get_db)):
    toko = (
        db.query(models.Toko)
        .options(
            joinedload(models.Toko.user),
            joinedload(models.Toko.produk).joinedload(models.Produk.kategori),
        )
        .filter(models.Toko.id == toko_id, models.Toko.status == "aktif")
        .first()
    )
    if not toko:
        raise HTTPException(status_code=404, detail="Toko tidak ditemukan")
    data = _serialize_toko_publik(db, toko)
    data["produk"] = [
        _serialize_produk_publik(db, p)
        for p in toko.produk
        if p.status == "aktif"
    ]
    return data


@publik_router.post(
    "/pesanan", status_code=status.HTTP_201_CREATED
)
def checkout_pesanan(
    payload: schemas.PesananCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_user),
):
    toko = (
        db.query(models.Toko)
        .filter(models.Toko.id == payload.toko_id)
        .first()
    )
    if not toko:
        raise HTTPException(status_code=404, detail="Toko tidak ditemukan")
    if toko.status != "aktif":
        raise HTTPException(
            status_code=400, detail="Toko belum aktif, tidak bisa menerima pesanan"
        )
    if not payload.nama_pembeli.strip():
        raise HTTPException(status_code=400, detail="Nama pembeli wajib diisi")
    if not payload.kontak_pembeli.strip():
        raise HTTPException(status_code=400, detail="Kontak pembeli wajib diisi")
    if not payload.alamat_pengiriman.strip():
        raise HTTPException(status_code=400, detail="Alamat pengiriman wajib diisi")
    if not payload.items:
        raise HTTPException(status_code=400, detail="Minimal satu produk dipilih")

    total_harga = 0
    detail = []
    for item in payload.items:
        if item.jumlah <= 0:
            raise HTTPException(
                status_code=400, detail="Jumlah produk harus lebih dari 0"
            )
        produk = (
            db.query(models.Produk)
            .filter(models.Produk.id == item.produk_id)
            .with_for_update()
            .first()
        )
        if not produk:
            raise HTTPException(
                status_code=404, detail=f"Produk id {item.produk_id} tidak ditemukan"
            )
        if produk.toko_id != toko.id:
            raise HTTPException(
                status_code=400,
                detail=f"Produk {produk.nama_produk} bukan milik toko ini",
            )
        if produk.status != "aktif":
            raise HTTPException(
                status_code=400,
                detail=f"Produk {produk.nama_produk} sedang tidak tersedia",
            )
        if produk.stok < item.jumlah:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Stok {produk.nama_produk} tidak cukup "
                    f"(tersedia {produk.stok}, diminta {item.jumlah})"
                ),
            )
        subtotal = produk.harga * item.jumlah
        total_harga += subtotal
        detail.append((produk, item.jumlah, subtotal))

    nomor_pesanan = _buat_nomor_pesanan(db)
    pesanan = models.Pesanan(
        nomor_pesanan=nomor_pesanan,
        pembeli_user_id=current_user.id if current_user else None,
        toko_id=toko.id,
        nama_pembeli=payload.nama_pembeli.strip(),
        kontak_pembeli=payload.kontak_pembeli.strip(),
        alamat_pengiriman=payload.alamat_pengiriman.strip(),
        total_harga=total_harga,
        status="menunggu_pembayaran",
        catatan_pembeli=payload.catatan_pembeli,
    )
    db.add(pesanan)
    db.flush()
    for produk, jumlah, subtotal in detail:
        db.add(
            models.ItemPesanan(
                pesanan_id=pesanan.id,
                produk_id=produk.id,
                nama_produk_saat_beli=produk.nama_produk,
                harga_saat_beli=produk.harga,
                jumlah=jumlah,
                subtotal=subtotal,
            )
        )
        produk.stok -= jumlah
    db.commit()
    db.refresh(pesanan)
    return _serialize_pesanan(db, pesanan)


@publik_router.post("/pesanan/{nomor_pesanan}/bukti-transfer")
async def upload_bukti_transfer(
    nomor_pesanan: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    pesanan = (
        db.query(models.Pesanan)
        .options(
            joinedload(models.Pesanan.toko).joinedload(models.Toko.user),
            joinedload(models.Pesanan.items),
        )
        .filter(models.Pesanan.nomor_pesanan == nomor_pesanan)
        .first()
    )
    if not pesanan:
        raise HTTPException(status_code=404, detail="Nomor pesanan tidak ditemukan")
    if pesanan.status != "menunggu_pembayaran":
        raise HTTPException(
            status_code=400,
            detail="Bukti transfer hanya bisa diupload untuk pesanan yang menunggu pembayaran",
        )
    ext, potongan = await _baca_file(
        file,
        models.BUKTI_TRANSFER_EXT_IZIN,
        models.BUKTI_TRANSFER_MAX_MB,
        "bukti transfer",
    )
    _hapus_file(pesanan.bukti_transfer_url)
    pesanan.bukti_transfer_url = _simpan_file(ext, potongan)
    pesanan.status = "menunggu_konfirmasi"
    db.commit()
    db.refresh(pesanan)
    return _serialize_pesanan(db, pesanan)


@publik_router.get("/pesanan/{nomor_pesanan}")
def get_pesanan_publik(nomor_pesanan: str, db: Session = Depends(get_db)):
    pesanan = (
        db.query(models.Pesanan)
        .options(
            joinedload(models.Pesanan.toko).joinedload(models.Toko.user),
            joinedload(models.Pesanan.items),
        )
        .filter(models.Pesanan.nomor_pesanan == nomor_pesanan)
        .first()
    )
    if not pesanan:
        raise HTTPException(status_code=404, detail="Nomor pesanan tidak ditemukan")
    return _serialize_pesanan(db, pesanan)


# =====================================================================
# Endpoint Penjual (JWT, role penjual)
# =====================================================================


@penjual_router.get("/toko")
def get_toko_saya(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = (
        db.query(models.Toko)
        .options(
            joinedload(models.Toko.user),
            joinedload(models.Toko.produk),
        )
        .filter(models.Toko.user_id == current_user.id)
        .first()
    )
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    return _serialize_toko(db, toko)


@penjual_router.post("/toko", status_code=status.HTTP_201_CREATED)
def buat_toko(
    payload: schemas.TokoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    if _get_toko_by_user(db, current_user.id):
        raise HTTPException(
            status_code=400, detail="Anda sudah punya toko (hanya boleh satu)"
        )
    _validasi_toko_payload(payload)
    toko = models.Toko(
        user_id=current_user.id,
        nama_toko=payload.nama_toko.strip(),
        deskripsi=payload.deskripsi,
        logo_url=payload.logo_url,
        nomor_rekening=payload.nomor_rekening.strip(),
        nama_bank=payload.nama_bank.strip(),
        nama_pemilik_rekening=payload.nama_pemilik_rekening.strip(),
        nomor_wa=payload.nomor_wa,
        alamat=payload.alamat,
        status="pending",
    )
    db.add(toko)
    db.commit()
    db.refresh(toko)
    return _serialize_toko(db, toko)


@penjual_router.put("/toko")
def ubah_toko(
    payload: schemas.TokoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    data = payload.model_dump(exclude_unset=True)
    _validasi_toko_update(data)
    for field, value in data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(toko, field, value)
    db.commit()
    db.refresh(toko)
    return _serialize_toko(db, toko)


def _validasi_toko_payload(payload: schemas.TokoCreate):
    if not payload.nama_toko.strip():
        raise HTTPException(status_code=400, detail="Nama toko wajib diisi")
    if not payload.nomor_rekening.strip():
        raise HTTPException(status_code=400, detail="Nomor rekening wajib diisi")
    if not payload.nama_bank.strip():
        raise HTTPException(status_code=400, detail="Nama bank wajib diisi")
    if not payload.nama_pemilik_rekening.strip():
        raise HTTPException(status_code=400, detail="Nama pemilik rekening wajib diisi")


def _validasi_toko_update(data: dict):
    if "nama_toko" in data and not (data["nama_toko"] or "").strip():
        raise HTTPException(status_code=400, detail="Nama toko wajib diisi")
    for field in ("nomor_rekening", "nama_bank", "nama_pemilik_rekening"):
        if field in data and not (data[field] or "").strip():
            raise HTTPException(status_code=400, detail=f"{field} tidak boleh kosong")


@penjual_router.get("/kategori")
def list_kategori_penjual(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_penjual),
):
    rows = db.query(models.KategoriProduk).order_by(models.KategoriProduk.id).all()
    return [
        {"id": k.id, "nama_kategori": k.nama_kategori}
        for k in rows
    ]


@penjual_router.get("/produk/{produk_id}")
def detail_produk_saya(
    produk_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    produk = (
        db.query(models.Produk)
        .options(joinedload(models.Produk.kategori))
        .filter(models.Produk.id == produk_id)
        .first()
    )
    if not produk:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    if produk.toko_id != toko.id:
        raise HTTPException(
            status_code=403, detail="Produk ini bukan milik toko Anda"
        )
    return _serialize_produk(db, produk)


@penjual_router.get("/produk")
def list_produk_saya(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    rows = (
        db.query(models.Produk)
        .options(joinedload(models.Produk.kategori))
        .filter(models.Produk.toko_id == toko.id)
        .order_by(models.Produk.id.desc())
        .all()
    )
    return [_serialize_produk(db, p) for p in rows]


@penjual_router.post("/produk", status_code=status.HTTP_201_CREATED)
async def buat_produk(
    kategori_id: int = Form(...),
    nama_produk: str = Form(...),
    harga: int = Form(...),
    stok: int = Form(0),
    deskripsi: Optional[str] = Form(default=None),
    foto: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    _get_kategori_or_404(db, kategori_id)
    _validasi_produk_fields(nama_produk, harga, stok)

    foto_url = None
    if foto:
        ext, potongan = await _baca_file(
            foto, models.FOTO_EXT_IZIN, models.FOTO_MAX_MB, "foto produk"
        )
        foto_url = _simpan_file(ext, potongan)

    produk = models.Produk(
        toko_id=toko.id,
        kategori_id=kategori_id,
        nama_produk=nama_produk.strip(),
        deskripsi=deskripsi,
        harga=harga,
        stok=stok,
        foto_url=foto_url,
        status="aktif",
    )
    db.add(produk)
    db.commit()
    db.refresh(produk)
    return _serialize_produk(db, produk)


@penjual_router.put("/produk/{produk_id}")
async def ubah_produk(
    produk_id: int,
    kategori_id: Optional[int] = Form(default=None),
    nama_produk: Optional[str] = Form(default=None),
    harga: Optional[int] = Form(default=None),
    stok: Optional[int] = Form(default=None),
    deskripsi: Optional[str] = Form(default=None),
    foto: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    produk = (
        db.query(models.Produk)
        .options(joinedload(models.Produk.kategori))
        .filter(models.Produk.id == produk_id)
        .first()
    )
    if not produk:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    if produk.toko_id != toko.id:
        raise HTTPException(
            status_code=403, detail="Produk ini bukan milik toko Anda"
        )

    if kategori_id is not None:
        _get_kategori_or_404(db, kategori_id)
        produk.kategori_id = kategori_id
    if nama_produk is not None:
        if not nama_produk.strip():
            raise HTTPException(status_code=400, detail="Nama produk wajib diisi")
        produk.nama_produk = nama_produk.strip()
    if harga is not None:
        if harga < 0:
            raise HTTPException(status_code=400, detail="Harga tidak boleh negatif")
        produk.harga = harga
    if stok is not None:
        if stok < 0:
            raise HTTPException(status_code=400, detail="Stok tidak boleh negatif")
        produk.stok = stok
    if deskripsi is not None:
        produk.deskripsi = deskripsi.strip() if deskripsi.strip() else None
    if foto:
        ext, potongan = await _baca_file(
            foto, models.FOTO_EXT_IZIN, models.FOTO_MAX_MB, "foto produk"
        )
        _hapus_file(produk.foto_url)
        produk.foto_url = _simpan_file(ext, potongan)

    db.commit()
    db.refresh(produk)
    return _serialize_produk(db, produk)


@penjual_router.delete("/produk/{produk_id}", status_code=status.HTTP_200_OK)
def nonaktifkan_produk(
    produk_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    produk = db.query(models.Produk).filter(models.Produk.id == produk_id).first()
    if not produk:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    if produk.toko_id != toko.id:
        raise HTTPException(
            status_code=403, detail="Produk ini bukan milik toko Anda"
        )

    dipakai = (
        db.query(models.ItemPesanan)
        .filter(models.ItemPesanan.produk_id == produk_id)
        .count()
    )
    if dipakai:
        produk.status = "nonaktif"
        db.commit()
        return {"message": "Produk dinonaktifkan (masih dipakai di pesanan lama)"}
    _hapus_file(produk.foto_url)
    db.delete(produk)
    db.commit()
    return {"message": "Produk dihapus"}


def _validasi_produk_fields(nama_produk: str, harga: int, stok: int):
    if not nama_produk.strip():
        raise HTTPException(status_code=400, detail="Nama produk wajib diisi")
    if harga < 0:
        raise HTTPException(status_code=400, detail="Harga tidak boleh negatif")
    if stok < 0:
        raise HTTPException(status_code=400, detail="Stok tidak boleh negatif")


@penjual_router.get("/pesanan")
def list_pesanan_penjual(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    query = (
        db.query(models.Pesanan)
        .options(
            joinedload(models.Pesanan.toko).joinedload(models.Toko.user),
            joinedload(models.Pesanan.items),
        )
        .filter(models.Pesanan.toko_id == toko.id)
    )
    if status_filter:
        if status_filter not in models.STATUS_PESANAN:
            raise HTTPException(status_code=400, detail="Status pesanan tidak valid")
        query = query.filter(models.Pesanan.status == status_filter)
    rows = query.order_by(models.Pesanan.id.desc()).all()
    return [_serialize_pesanan(db, p) for p in rows]


@penjual_router.patch("/pesanan/{pesanan_id}/konfirmasi-pembayaran")
def konfirmasi_pembayaran(
    pesanan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    pesanan = _get_pesanan_owned(db, pesanan_id, toko.id)
    if pesanan.status != "menunggu_konfirmasi":
        raise HTTPException(
            status_code=400,
            detail="Pesanan ini tidak sedang menunggu konfirmasi pembayaran",
        )
    if not pesanan.bukti_transfer_url:
        raise HTTPException(
            status_code=400,
            detail="Pembeli belum mengupload bukti transfer",
        )
    pesanan.status = "diproses"
    db.commit()
    db.refresh(pesanan)
    return _serialize_pesanan(db, pesanan)


@penjual_router.patch("/pesanan/{pesanan_id}/status")
def ubah_status_pesanan(
    pesanan_id: int,
    payload: schemas.PesananStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")
    pesanan = _get_pesanan_owned(db, pesanan_id, toko.id)
    transisi = {
        "menunggu_konfirmasi": ("diproses", "dibatalkan"),
        "diproses": ("dikirim", "dibatalkan"),
        "dikirim": ("selesai",),
        "selesai": (),
        "menunggu_pembayaran": ("dibatalkan",),
    }
    if payload.status not in models.STATUS_PESANAN:
        raise HTTPException(status_code=400, detail="Status pesanan tidak valid")
    if payload.status not in transisi.get(pesanan.status, ()):
        raise HTTPException(
            status_code=400,
            detail=f"Tidak bisa mengubah status dari {pesanan.status} ke {payload.status}",
        )
    pesanan.status = payload.status
    db.commit()
    db.refresh(pesanan)
    return _serialize_pesanan(db, pesanan)


@penjual_router.get("/dashboard")
def dashboard_penjual(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_penjual),
):
    toko = _get_toko_by_user(db, current_user.id)
    if not toko:
        raise HTTPException(status_code=404, detail="Toko belum dibuat")

    tahun = date.today().year
    bulan = date.today().month
    jumlah_produk = (
        db.query(models.Produk)
        .filter(models.Produk.toko_id == toko.id, models.Produk.status == "aktif")
        .count()
    )
    menunggu_konfirmasi = (
        db.query(models.Pesanan)
        .filter(
            models.Pesanan.toko_id == toko.id,
            models.Pesanan.status == "menunggu_konfirmasi",
        )
        .count()
    )
    total_penjualan_bulan_ini = (
        db.query(func.coalesce(func.sum(models.Pesanan.total_harga), 0))
        .filter(
            models.Pesanan.toko_id == toko.id,
            func.extract("year", models.Pesanan.created_at) == tahun,
            func.extract("month", models.Pesanan.created_at) == bulan,
            models.Pesanan.status.in_(
                ("menunggu_konfirmasi", "diproses", "dikirim", "selesai")
            ),
        )
        .scalar()
    )
    return {
        "status_toko": toko.status,
        "jumlah_produk": jumlah_produk,
        "pesanan_menunggu_konfirmasi": menunggu_konfirmasi,
        "total_penjualan_bulan_ini": total_penjualan_bulan_ini,
    }


# =====================================================================
# Endpoint Admin Marketplace (JWT, role admin)
# =====================================================================


@admin_router.get("/toko")
def list_toko_admin(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    query = (
        db.query(models.Toko)
        .options(
            joinedload(models.Toko.user),
            joinedload(models.Toko.produk),
        )
    )
    if status_filter:
        if status_filter not in models.STATUS_TOKO:
            raise HTTPException(status_code=400, detail="Status toko tidak valid")
        query = query.filter(models.Toko.status == status_filter)
    rows = query.order_by(models.Toko.created_at.desc()).all()
    return [_serialize_toko(db, t) for t in rows]


@admin_router.patch("/toko/{toko_id}/verifikasi")
def verifikasi_toko(
    toko_id: int,
    payload: schemas.TokoVerifikasi,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if payload.status not in ("aktif", "nonaktif"):
        raise HTTPException(status_code=400, detail="Status verifikasi tidak valid")
    toko = (
        db.query(models.Toko)
        .options(joinedload(models.Toko.user))
        .filter(models.Toko.id == toko_id)
        .first()
    )
    if not toko:
        raise HTTPException(status_code=404, detail="Toko tidak ditemukan")
    toko.status = payload.status
    db.commit()
    db.refresh(toko)
    return _serialize_toko(db, toko)


@admin_router.get("/kategori-produk")
def list_kategori_produk(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    rows = db.query(models.KategoriProduk).order_by(models.KategoriProduk.id).all()
    return [
        {
            "id": k.id,
            "nama_kategori": k.nama_kategori,
            "created_at": k.created_at,
        }
        for k in rows
    ]


@admin_router.post(
    "/kategori-produk",
    status_code=status.HTTP_201_CREATED,
)
def buat_kategori_produk(
    payload: schemas.KategoriProdukCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    if not payload.nama_kategori.strip():
        raise HTTPException(status_code=400, detail="Nama kategori wajib diisi")
    nama = payload.nama_kategori.strip()
    if (
        db.query(models.KategoriProduk)
        .filter(models.KategoriProduk.nama_kategori == nama)
        .first()
    ):
        raise HTTPException(status_code=400, detail="Nama kategori sudah digunakan")
    obj = models.KategoriProduk(nama_kategori=nama)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "nama_kategori": obj.nama_kategori, "created_at": obj.created_at}


@admin_router.put("/kategori-produk/{kategori_id}")
def ubah_kategori_produk(
    kategori_id: int,
    payload: schemas.KategoriProdukUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kategori_or_404(db, kategori_id)
    nama = (payload.nama_kategori or "").strip()
    if not nama:
        raise HTTPException(status_code=400, detail="Nama kategori wajib diisi")
    if (
        db.query(models.KategoriProduk)
        .filter(
            models.KategoriProduk.nama_kategori == nama,
            models.KategoriProduk.id != kategori_id,
        )
        .first()
    ):
        raise HTTPException(status_code=400, detail="Nama kategori sudah digunakan")
    obj.nama_kategori = nama
    db.commit()
    db.refresh(obj)
    return {"id": obj.id, "nama_kategori": obj.nama_kategori, "created_at": obj.created_at}


@admin_router.delete("/kategori-produk/{kategori_id}", status_code=status.HTTP_200_OK)
def hapus_kategori_produk(
    kategori_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    obj = _get_kategori_or_404(db, kategori_id)
    dipakai = (
        db.query(models.Produk)
        .filter(models.Produk.kategori_id == kategori_id)
        .count()
    )
    if dipakai:
        raise HTTPException(
            status_code=400,
            detail=f"Kategori masih dipakai oleh {dipakai} produk",
        )
    db.delete(obj)
    db.commit()
    return {"message": "Kategori dihapus"}


@admin_router.get("/rekap")
def rekap_marketplace(
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    tahun = date.today().year
    bulan = date.today().month

    toko_aktif = (
        db.query(models.Toko).filter(models.Toko.status == "aktif").count()
    )
    toko_pending = (
        db.query(models.Toko).filter(models.Toko.status == "pending").count()
    )
    total_produk = (
        db.query(models.Produk).filter(models.Produk.status == "aktif").count()
    )
    total_transaksi = (
        db.query(models.Pesanan)
        .filter(
            func.extract("year", models.Pesanan.created_at) == tahun,
            func.extract("month", models.Pesanan.created_at) == bulan,
            models.Pesanan.status.in_(
                ("menunggu_konfirmasi", "diproses", "dikirim", "selesai")
            ),
        )
        .count()
    )
    estimasi_nilai_transaksi = (
        db.query(func.coalesce(func.sum(models.Pesanan.total_harga), 0))
        .filter(
            func.extract("year", models.Pesanan.created_at) == tahun,
            func.extract("month", models.Pesanan.created_at) == bulan,
            models.Pesanan.status.in_(
                ("menunggu_konfirmasi", "diproses", "dikirim", "selesai")
            ),
        )
        .scalar()
    )
    return {
        "toko_aktif": toko_aktif,
        "toko_pending": toko_pending,
        "total_produk": total_produk,
        "total_transaksi": total_transaksi,
        "estimasi_nilai_transaksi": estimasi_nilai_transaksi,
    }
