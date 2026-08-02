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
from app.deps import get_current_admin, get_current_user

router = APIRouter(prefix="/admin", tags=["pelaporan"])


# ---------- Helper ----------


def _cek_role(current_user: models.User):
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Butuh role admin atau staff",
        )


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


async def _baca_file(file: UploadFile) -> tuple:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in models.BUKTI_EXT_IZIN:
        raise HTTPException(
            status_code=400,
            detail="Tipe file tidak diizinkan (pdf, jpg, jpeg, png, docx)",
        )
    ukuran = 0
    potongan = []
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        ukuran += len(chunk)
        potongan.append(chunk)
        if ukuran > models.BUKTI_MAX_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Ukuran file melebihi {models.BUKTI_MAX_MB} MB",
            )
    if not potongan:
        raise HTTPException(status_code=400, detail="File kosong")
    return ext, potongan


def _get_program_or_404(db: Session, pk_id: int) -> models.ProgramKerja:
    obj = (
        db.query(models.ProgramKerja)
        .options(joinedload(models.ProgramKerja.bidang))
        .filter(models.ProgramKerja.id == pk_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Program kerja tidak ditemukan")
    return obj


def _get_anggaran_or_404(db: Session, ap_id: int) -> models.AnggaranProgram:
    obj = (
        db.query(models.AnggaranProgram)
        .options(joinedload(models.AnggaranProgram.program_kerja))
        .filter(models.AnggaranProgram.id == ap_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Alokasi anggaran tidak ditemukan")
    return obj


def _get_realisasi_or_404(db: Session, realisasi_id: int) -> models.RealisasiAnggaran:
    obj = (
        db.query(models.RealisasiAnggaran)
        .options(joinedload(models.RealisasiAnggaran.anggaran_program))
        .filter(models.RealisasiAnggaran.id == realisasi_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Realisasi anggaran tidak ditemukan")
    return obj


def _get_laporan_or_404(db: Session, laporan_id: int) -> models.LaporanKegiatan:
    obj = (
        db.query(models.LaporanKegiatan)
        .options(joinedload(models.LaporanKegiatan.kegiatan))
        .filter(models.LaporanKegiatan.id == laporan_id)
        .first()
    )
    if not obj:
        raise HTTPException(status_code=404, detail="Laporan kegiatan tidak ditemukan")
    return obj


def _sum_disetujui(db: Session, ap_id: int) -> int:
    return (
        db.query(func.coalesce(func.sum(models.RealisasiAnggaran.jumlah_realisasi), 0))
        .filter(
            models.RealisasiAnggaran.anggaran_program_id == ap_id,
            models.RealisasiAnggaran.status == "disetujui",
        )
        .scalar()
    )


def _cek_sumber_dana(sumber_dana: str):
    if sumber_dana not in models.SUMBER_DANA:
        raise HTTPException(status_code=400, detail="Sumber dana tidak valid")


def _persen_penyerapan(jumlah_anggaran: int, total_realisasi: int) -> float:
    if not jumlah_anggaran or jumlah_anggaran <= 0:
        return 0.0
    return round(min(100.0, total_realisasi / jumlah_anggaran * 100), 2)


def _serialize_anggaran(db: Session, ap: models.AnggaranProgram) -> dict:
    data = schemas.AnggaranProgramOut.model_validate(ap).model_dump()
    data["judul_program_kerja"] = ap.program_kerja.judul if ap.program_kerja else ""
    data["nama_bidang"] = (
        ap.program_kerja.bidang.nama_bidang
        if ap.program_kerja and ap.program_kerja.bidang
        else ""
    )
    data["total_realisasi"] = _sum_disetujui(db, ap.id)
    data["persen_penyerapan"] = _persen_penyerapan(
        ap.jumlah_anggaran, data["total_realisasi"]
    )
    return data


def _serialize_realisasi(db: Session, r: models.RealisasiAnggaran) -> dict:
    data = schemas.RealisasiAnggaranOut.model_validate(r).model_dump()
    data["nama_diinput"] = r.diinput_oleh_user.nama_lengkap if r.diinput_oleh_user else ""
    data["nama_direview"] = r.direview_oleh_user.nama_lengkap if r.direview_oleh_user else ""
    data["program_kerja_id"] = r.anggaran_program.program_kerja_id if r.anggaran_program else None
    data["judul_program_kerja"] = (
        r.anggaran_program.program_kerja.judul if r.anggaran_program and r.anggaran_program.program_kerja else ""
    )
    data["nama_bidang"] = (
        r.anggaran_program.program_kerja.bidang.nama_bidang
        if r.anggaran_program
        and r.anggaran_program.program_kerja
        and r.anggaran_program.program_kerja.bidang
        else ""
    )
    data["tahun_anggaran"] = r.anggaran_program.tahun_anggaran if r.anggaran_program else None
    data["jumlah_anggaran"] = r.anggaran_program.jumlah_anggaran if r.anggaran_program else None
    return data


def _serialize_laporan(db: Session, l: models.LaporanKegiatan) -> dict:
    data = schemas.LaporanKegiatanOut.model_validate(l).model_dump()
    data["nama_kegiatan"] = l.kegiatan.judul if l.kegiatan else ""
    data["nama_dibuat"] = l.dibuat_oleh_user.nama_lengkap if l.dibuat_oleh_user else ""
    return data


# ---------- Alokasi Anggaran ----------


@router.get("/anggaran-program")
def list_anggaran_program(
    tahun_anggaran: Optional[int] = Query(default=None),
    program_kerja_id: Optional[int] = Query(default=None),
    bidang_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    query = db.query(models.AnggaranProgram).options(
        joinedload(models.AnggaranProgram.program_kerja).joinedload(
            models.ProgramKerja.bidang
        )
    )
    if tahun_anggaran is not None:
        query = query.filter(models.AnggaranProgram.tahun_anggaran == tahun_anggaran)
    if program_kerja_id is not None:
        query = query.filter(models.AnggaranProgram.program_kerja_id == program_kerja_id)
    if bidang_id is not None:
        query = query.join(
            models.ProgramKerja,
            models.ProgramKerja.id == models.AnggaranProgram.program_kerja_id,
        ).filter(models.ProgramKerja.bidang_id == bidang_id)
    rows = query.order_by(
        models.AnggaranProgram.tahun_anggaran.desc(), models.AnggaranProgram.id.desc()
    ).all()
    return [_serialize_anggaran(db, ap) for ap in rows]


@router.post(
    "/anggaran-program",
    response_model=schemas.AnggaranProgramOut,
    status_code=status.HTTP_201_CREATED,
)
def create_anggaran_program(
    payload: schemas.AnggaranProgramCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    _get_program_or_404(db, payload.program_kerja_id)
    _cek_sumber_dana(payload.sumber_dana)
    if payload.tahun_anggaran <= 0:
        raise HTTPException(status_code=400, detail="Tahun anggaran tidak valid")
    if payload.jumlah_anggaran <= 0:
        raise HTTPException(status_code=400, detail="Jumlah anggaran harus lebih dari 0")
    duplikat = (
        db.query(models.AnggaranProgram)
        .filter(
            models.AnggaranProgram.program_kerja_id == payload.program_kerja_id,
            models.AnggaranProgram.tahun_anggaran == payload.tahun_anggaran,
        )
        .first()
    )
    if duplikat:
        raise HTTPException(
            status_code=400,
            detail="Program kerja ini sudah punya alokasi anggaran untuk tahun tersebut",
        )
    obj = models.AnggaranProgram(
        program_kerja_id=payload.program_kerja_id,
        tahun_anggaran=payload.tahun_anggaran,
        jumlah_anggaran=payload.jumlah_anggaran,
        sumber_dana=payload.sumber_dana,
        catatan=payload.catatan,
        created_by=current_user.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/anggaran-program/{ap_id}", response_model=schemas.AnggaranProgramOut)
def update_anggaran_program(
    ap_id: int,
    payload: schemas.AnggaranProgramUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_anggaran_or_404(db, ap_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("program_kerja_id"):
        _get_program_or_404(db, data["program_kerja_id"])
    if data.get("sumber_dana"):
        _cek_sumber_dana(data["sumber_dana"])
    if data.get("tahun_anggaran") is not None and data["tahun_anggaran"] <= 0:
        raise HTTPException(status_code=400, detail="Tahun anggaran tidak valid")

    program_kerja_id = data.get("program_kerja_id", obj.program_kerja_id)
    tahun_anggaran = data.get("tahun_anggaran", obj.tahun_anggaran)
    duplikat = (
        db.query(models.AnggaranProgram)
        .filter(
            models.AnggaranProgram.program_kerja_id == program_kerja_id,
            models.AnggaranProgram.tahun_anggaran == tahun_anggaran,
            models.AnggaranProgram.id != ap_id,
        )
        .first()
    )
    if duplikat:
        raise HTTPException(
            status_code=400,
            detail="Program kerja ini sudah punya alokasi anggaran untuk tahun tersebut",
        )

    jumlah_baru = data.get("jumlah_anggaran", obj.jumlah_anggaran)
    if jumlah_baru <= 0:
        raise HTTPException(status_code=400, detail="Jumlah anggaran harus lebih dari 0")
    terpakai = _sum_disetujui(db, ap_id)
    if jumlah_baru < terpakai:
        raise HTTPException(
            status_code=400,
            detail=f"Jumlah anggaran tidak boleh lebih kecil dari realisasi yang sudah disetujui ({terpakai})",
        )

    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/anggaran-program/{ap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anggaran_program(
    ap_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_anggaran_or_404(db, ap_id)
    if (
        db.query(models.RealisasiAnggaran)
        .filter(models.RealisasiAnggaran.anggaran_program_id == ap_id)
        .count()
    ):
        raise HTTPException(
            status_code=400,
            detail="Tidak bisa dihapus: alokasi anggaran ini sudah punya catatan realisasi",
        )
    db.delete(obj)
    db.commit()


# ---------- Realisasi Anggaran ----------


@router.get("/anggaran-program/{ap_id}/realisasi")
def list_realisasi_anggaran(
    ap_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    _get_anggaran_or_404(db, ap_id)
    rows = (
        db.query(models.RealisasiAnggaran)
        .options(
            joinedload(models.RealisasiAnggaran.diinput_oleh_user),
            joinedload(models.RealisasiAnggaran.direview_oleh_user),
            joinedload(models.RealisasiAnggaran.anggaran_program)
            .joinedload(models.AnggaranProgram.program_kerja)
            .joinedload(models.ProgramKerja.bidang),
        )
        .filter(models.RealisasiAnggaran.anggaran_program_id == ap_id)
        .order_by(
            models.RealisasiAnggaran.tanggal_realisasi.asc(),
            models.RealisasiAnggaran.id.asc(),
        )
        .all()
    )
    return [_serialize_realisasi(db, r) for r in rows]


@router.post(
    "/anggaran-program/{ap_id}/realisasi",
    response_model=schemas.RealisasiAnggaranOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_realisasi_anggaran(
    ap_id: int,
    tanggal_realisasi: date = Form(...),
    jumlah_realisasi: int = Form(...),
    keterangan: str = Form(...),
    bukti: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    ap = _get_anggaran_or_404(db, ap_id)
    if jumlah_realisasi <= 0:
        raise HTTPException(status_code=400, detail="Jumlah realisasi harus lebih dari 0")
    if not keterangan.strip():
        raise HTTPException(status_code=400, detail="Keterangan wajib diisi")

    terpakai = _sum_disetujui(db, ap_id)
    if terpakai + jumlah_realisasi > ap.jumlah_anggaran:
        sisa = ap.jumlah_anggaran - terpakai
        raise HTTPException(
            status_code=400,
            detail=(
                f"Melebihi alokasi anggaran. Terpakai {terpakai}, sisa {sisa}, "
                f"tapi realisasi yang diajukan {jumlah_realisasi}."
            ),
        )

    ext, potongan = await _baca_file(bukti)
    obj = models.RealisasiAnggaran(
        anggaran_program_id=ap_id,
        tanggal_realisasi=tanggal_realisasi,
        jumlah_realisasi=jumlah_realisasi,
        keterangan=keterangan.strip(),
        bukti_url=_simpan_file(ext, potongan),
        status="diajukan",
        diinput_oleh=current_user.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/realisasi/{realisasi_id}/bukti")
async def upload_bukti_realisasi(
    realisasi_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_realisasi_or_404(db, realisasi_id)
    if obj.status == "disetujui":
        raise HTTPException(
            status_code=400, detail="Realisasi sudah disetujui, tidak bisa ganti bukti"
        )
    ext, potongan = await _baca_file(file)
    _hapus_file(obj.bukti_url)
    obj.bukti_url = _simpan_file(ext, potongan)
    db.commit()
    db.refresh(obj)
    return _serialize_realisasi(db, obj)


@router.patch("/realisasi/{realisasi_id}/review")
def review_realisasi(
    realisasi_id: int,
    payload: schemas.RealisasiReview,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
):
    obj = _get_realisasi_or_404(db, realisasi_id)
    if obj.status != "diajukan":
        raise HTTPException(
            status_code=400, detail="Hanya realisasi berstatus diajukan yang bisa direview"
        )
    if payload.status not in ("disetujui", "ditolak"):
        raise HTTPException(status_code=400, detail="Status review tidak valid")
    if payload.status == "ditolak" and not (payload.catatan_review or "").strip():
        raise HTTPException(
            status_code=400, detail="Catatan review wajib diisi saat menolak realisasi"
        )

    if payload.status == "disetujui":
        terpakai = (
            db.query(func.coalesce(func.sum(models.RealisasiAnggaran.jumlah_realisasi), 0))
            .filter(
                models.RealisasiAnggaran.anggaran_program_id == obj.anggaran_program_id,
                models.RealisasiAnggaran.status == "disetujui",
                models.RealisasiAnggaran.id != obj.id,
            )
            .scalar()
        )
        if terpakai + obj.jumlah_realisasi > obj.anggaran_program.jumlah_anggaran:
            sisa = obj.anggaran_program.jumlah_anggaran - terpakai
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Menyetujui realisasi ini akan melebihi alokasi anggaran. "
                    f"Sisa kuota tersisa {sisa}."
                ),
            )

    obj.status = payload.status
    obj.catatan_review = payload.catatan_review
    obj.direview_oleh = current_admin.id
    db.commit()
    db.refresh(obj)
    return _serialize_realisasi(db, obj)


# ---------- Laporan Kegiatan ----------


@router.get("/laporan-kegiatan")
def list_laporan_kegiatan(
    kegiatan_id: Optional[int] = Query(default=None),
    tanggal_dari: Optional[date] = Query(default=None),
    tanggal_sampai: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    query = db.query(models.LaporanKegiatan).options(
        joinedload(models.LaporanKegiatan.kegiatan),
        joinedload(models.LaporanKegiatan.dibuat_oleh_user),
    )
    if kegiatan_id is not None:
        query = query.filter(models.LaporanKegiatan.kegiatan_id == kegiatan_id)
    if tanggal_dari:
        query = query.filter(models.LaporanKegiatan.tanggal_laporan >= tanggal_dari)
    if tanggal_sampai:
        query = query.filter(models.LaporanKegiatan.tanggal_laporan <= tanggal_sampai)
    rows = query.order_by(
        models.LaporanKegiatan.tanggal_laporan.desc(),
        models.LaporanKegiatan.id.desc(),
    ).all()
    return [_serialize_laporan(db, l) for l in rows]


@router.post(
    "/laporan-kegiatan",
    response_model=schemas.LaporanKegiatanOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_laporan_kegiatan(
    kegiatan_id: int = Form(...),
    judul_laporan: str = Form(...),
    ringkasan_pelaksanaan: str = Form(...),
    jumlah_peserta: Optional[int] = Form(default=None),
    kendala: Optional[str] = Form(default=None),
    rekomendasi: Optional[str] = Form(default=None),
    tanggal_laporan: date = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    kegiatan = (
        db.query(models.Kegiatan)
        .filter(models.Kegiatan.id == kegiatan_id)
        .first()
    )
    if not kegiatan:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    if kegiatan.status != "selesai":
        raise HTTPException(
            status_code=400,
            detail="Laporan hanya bisa dibuat untuk kegiatan yang sudah selesai",
        )
    sudah_ada = (
        db.query(models.LaporanKegiatan)
        .filter(models.LaporanKegiatan.kegiatan_id == kegiatan_id)
        .first()
    )
    if sudah_ada:
        raise HTTPException(
            status_code=400, detail="Kegiatan ini sudah punya laporan"
        )
    if not judul_laporan.strip():
        raise HTTPException(status_code=400, detail="Judul laporan wajib diisi")
    if not ringkasan_pelaksanaan.strip():
        raise HTTPException(status_code=400, detail="Ringkasan pelaksanaan wajib diisi")

    ext, potongan = await _baca_file(file)
    obj = models.LaporanKegiatan(
        kegiatan_id=kegiatan_id,
        judul_laporan=judul_laporan.strip(),
        ringkasan_pelaksanaan=ringkasan_pelaksanaan.strip(),
        jumlah_peserta=jumlah_peserta,
        kendala=kendala,
        rekomendasi=rekomendasi,
        file_laporan_url=_simpan_file(ext, potongan),
        tanggal_laporan=tanggal_laporan,
        dibuat_oleh=current_user.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/laporan-kegiatan/{laporan_id}")
def get_laporan_kegiatan(
    laporan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_laporan_or_404(db, laporan_id)
    return _serialize_laporan(db, obj)


@router.put(
    "/laporan-kegiatan/{laporan_id}", response_model=schemas.LaporanKegiatanOut
)
def update_laporan_kegiatan(
    laporan_id: int,
    payload: schemas.LaporanKegiatanUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_laporan_or_404(db, laporan_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/laporan-kegiatan/{laporan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_laporan_kegiatan(
    laporan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_laporan_or_404(db, laporan_id)
    _hapus_file(obj.file_laporan_url)
    db.delete(obj)
    db.commit()


@router.post("/laporan-kegiatan/{laporan_id}/file")
async def upload_file_laporan(
    laporan_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    obj = _get_laporan_or_404(db, laporan_id)
    ext, potongan = await _baca_file(file)
    _hapus_file(obj.file_laporan_url)
    obj.file_laporan_url = _simpan_file(ext, potongan)
    db.commit()
    db.refresh(obj)
    return _serialize_laporan(db, obj)


# ---------- Dashboard & Rekap ----------


@router.get("/pelaporan/rekap-anggaran")
def rekap_anggaran(
    tahun: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    tahun = tahun or date.today().year

    anggaran_rows = (
        db.query(
            models.AnggaranProgram,
            models.ProgramKerja.bidang_id,
            models.BidangKwarda.nama_bidang,
        )
        .join(
            models.ProgramKerja,
            models.ProgramKerja.id == models.AnggaranProgram.program_kerja_id,
        )
        .join(
            models.BidangKwarda,
            models.BidangKwarda.id == models.ProgramKerja.bidang_id,
        )
        .filter(models.AnggaranProgram.tahun_anggaran == tahun)
        .all()
    )
    sums = dict(
        db.query(
            models.RealisasiAnggaran.anggaran_program_id,
            func.sum(models.RealisasiAnggaran.jumlah_realisasi),
        )
        .filter(models.RealisasiAnggaran.status == "disetujui")
        .group_by(models.RealisasiAnggaran.anggaran_program_id)
        .all()
    )

    total_anggaran = 0
    total_realisasi = 0
    per_bidang = {}
    for ap, bidang_id, nama_bidang in anggaran_rows:
        total_anggaran += ap.jumlah_anggaran
        approved = sums.get(ap.id, 0) or 0
        total_realisasi += approved
        entry = per_bidang.setdefault(
            bidang_id,
            {
                "bidang_id": bidang_id,
                "nama_bidang": nama_bidang,
                "total_anggaran": 0,
                "total_realisasi": 0,
            },
        )
        entry["total_anggaran"] += ap.jumlah_anggaran
        entry["total_realisasi"] += approved

    per_bidang_list = []
    for entry in per_bidang.values():
        entry["persen_penyerapan"] = _persen_penyerapan(
            entry["total_anggaran"], entry["total_realisasi"]
        )
        per_bidang_list.append(entry)
    per_bidang_list.sort(key=lambda x: x["total_anggaran"], reverse=True)

    return {
        "tahun": tahun,
        "total_anggaran": total_anggaran,
        "total_realisasi": total_realisasi,
        "persen_penyerapan": _persen_penyerapan(total_anggaran, total_realisasi),
        "per_bidang": per_bidang_list,
    }


@router.get("/pelaporan/rekap-kegiatan")
def rekap_kegiatan_pelaporan(
    tahun: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    tahun = tahun or date.today().year

    def _count(extra=None):
        q = db.query(models.Kegiatan).filter(
            func.extract("year", models.Kegiatan.tanggal_mulai) == tahun
        )
        if extra is not None:
            q = q.filter(extra)
        return q.count()

    total_direncanakan = (
        db.query(models.Kegiatan)
        .filter(
            func.extract("year", models.Kegiatan.tanggal_mulai) == tahun,
            models.Kegiatan.status.in_(("rencana", "berjalan", "selesai")),
        )
        .count()
    )
    jumlah_selesai = _count(models.Kegiatan.status == "selesai")
    persen = (
        round(jumlah_selesai / total_direncanakan * 100, 2)
        if total_direncanakan
        else 0.0
    )
    per_status = {}
    for s in models.PROGRAM_STATUS:
        per_status[s] = _count(models.Kegiatan.status == s)

    return {
        "tahun": tahun,
        "total_direncanakan": total_direncanakan,
        "jumlah_selesai": jumlah_selesai,
        "persen_capaian": persen,
        "per_status": per_status,
    }


@router.get("/pelaporan/realisasi-pending")
def list_realisasi_pending(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _cek_role(current_user)
    rows = (
        db.query(models.RealisasiAnggaran)
        .options(
            joinedload(models.RealisasiAnggaran.diinput_oleh_user),
            joinedload(models.RealisasiAnggaran.direview_oleh_user),
            joinedload(models.RealisasiAnggaran.anggaran_program)
            .joinedload(models.AnggaranProgram.program_kerja)
            .joinedload(models.ProgramKerja.bidang),
        )
        .filter(models.RealisasiAnggaran.status == "diajukan")
        .order_by(models.RealisasiAnggaran.created_at.asc())
        .all()
    )
    return [_serialize_realisasi(db, r) for r in rows]
