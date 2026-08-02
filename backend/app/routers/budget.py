from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_admin, get_current_user

router = APIRouter(tags=["budget"])


def _get_program_or_404(db: Session, program_id: int) -> models.ProgramKerja:
    program = db.query(models.ProgramKerja).filter(models.ProgramKerja.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program kerja tidak ditemukan",
        )
    return program


def _get_anggaran_or_404(db: Session, anggaran_id: int) -> models.Anggaran:
    anggaran = db.query(models.Anggaran).filter(models.Anggaran.id == anggaran_id).first()
    if not anggaran:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anggaran tidak ditemukan",
        )
    return anggaran


def _get_rencana_or_404(db: Session, rencana_id: int) -> models.RencanaBiaya:
    rencana = db.query(models.RencanaBiaya).filter(models.RencanaBiaya.id == rencana_id).first()
    if not rencana:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rencana biaya tidak ditemukan",
        )
    return rencana


def _get_realisasi_or_404(db: Session, realisasi_id: int) -> models.RealisasiPengeluaran:
    realisasi = db.query(models.RealisasiPengeluaran).filter(models.RealisasiPengeluaran.id == realisasi_id).first()
    if not realisasi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Realisasi pengeluaran tidak ditemukan",
        )
    return realisasi


@router.get("/program", response_model=List[schemas.ProgramKerjaOut])
def list_programs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user
    return db.query(models.ProgramKerja).order_by(models.ProgramKerja.id).all()


@router.post("/program", response_model=schemas.ProgramKerjaOut, status_code=status.HTTP_201_CREATED)
def create_program(
    payload: schemas.ProgramKerjaCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    program = models.ProgramKerja(
        nama_program=payload.nama_program,
        tahun_pelaksanaan=payload.tahun_pelaksanaan,
        penanggung_jawab=payload.penanggung_jawab,
        status=payload.status,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.get("/program/{program_id}", response_model=schemas.ProgramKerjaOut)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user
    return _get_program_or_404(db, program_id)


@router.put("/program/{program_id}", response_model=schemas.ProgramKerjaOut)
def update_program(
    program_id: int,
    payload: schemas.ProgramKerjaUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    program = _get_program_or_404(db, program_id)

    if payload.nama_program is not None:
        program.nama_program = payload.nama_program
    if payload.tahun_pelaksanaan is not None:
        program.tahun_pelaksanaan = payload.tahun_pelaksanaan
    if payload.penanggung_jawab is not None:
        program.penanggung_jawab = payload.penanggung_jawab
    if payload.status is not None:
        program.status = payload.status

    db.commit()
    db.refresh(program)
    return program


@router.delete("/program/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    program = _get_program_or_404(db, program_id)
    db.delete(program)
    db.commit()


@router.get("/anggaran", response_model=List[schemas.AnggaranOut])
def list_anggaran(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user
    return db.query(models.Anggaran).order_by(models.Anggaran.id).all()


@router.post("/anggaran", response_model=schemas.AnggaranOut, status_code=status.HTTP_201_CREATED)
def create_anggaran(
    payload: schemas.AnggaranCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_program_or_404(db, payload.program_id)

    if payload.pagu_anggaran <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pagu anggaran harus lebih dari nol",
        )

    anggaran = models.Anggaran(
        kode_anggaran=payload.kode_anggaran,
        nama_anggaran=payload.nama_anggaran,
        pagu_anggaran=payload.pagu_anggaran,
        status=payload.status,
        program_id=payload.program_id,
    )
    db.add(anggaran)
    db.commit()
    db.refresh(anggaran)
    return anggaran


@router.get("/anggaran/{anggaran_id}", response_model=schemas.AnggaranOut)
def get_anggaran(
    anggaran_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user
    return _get_anggaran_or_404(db, anggaran_id)


@router.put("/anggaran/{anggaran_id}", response_model=schemas.AnggaranOut)
def update_anggaran(
    anggaran_id: int,
    payload: schemas.AnggaranUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    anggaran = _get_anggaran_or_404(db, anggaran_id)

    if payload.program_id is not None:
        _get_program_or_404(db, payload.program_id)
        anggaran.program_id = payload.program_id
    if payload.kode_anggaran is not None:
        anggaran.kode_anggaran = payload.kode_anggaran
    if payload.nama_anggaran is not None:
        anggaran.nama_anggaran = payload.nama_anggaran
    if payload.pagu_anggaran is not None:
        if payload.pagu_anggaran <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pagu anggaran harus lebih dari nol",
            )
        anggaran.pagu_anggaran = payload.pagu_anggaran
    if payload.status is not None:
        anggaran.status = payload.status

    db.commit()
    db.refresh(anggaran)
    return anggaran


@router.delete("/anggaran/{anggaran_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_anggaran(
    anggaran_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    anggaran = _get_anggaran_or_404(db, anggaran_id)
    db.delete(anggaran)
    db.commit()


@router.get("/rencana", response_model=List[schemas.RencanaBiayaOut])
def list_rencana(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user
    return db.query(models.RencanaBiaya).order_by(models.RencanaBiaya.id).all()


@router.post("/rencana", response_model=schemas.RencanaBiayaOut, status_code=status.HTTP_201_CREATED)
def create_rencana(
    payload: schemas.RencanaBiayaCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    _get_anggaran_or_404(db, payload.anggaran_id)

    if payload.volume <= 0 or payload.harga_satuan <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Volume dan harga satuan harus bernilai positif",
        )

    subtotal = payload.volume * payload.harga_satuan
    rencana = models.RencanaBiaya(
        nama_item=payload.nama_item,
        volume=payload.volume,
        satuan=payload.satuan,
        harga_satuan=payload.harga_satuan,
        subtotal=subtotal,
        anggaran_id=payload.anggaran_id,
    )
    db.add(rencana)
    db.commit()
    db.refresh(rencana)
    return rencana


@router.put("/rencana/{rencana_id}", response_model=schemas.RencanaBiayaOut)
def update_rencana(
    rencana_id: int,
    payload: schemas.RencanaBiayaUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    rencana = _get_rencana_or_404(db, rencana_id)

    if payload.anggaran_id is not None:
        _get_anggaran_or_404(db, payload.anggaran_id)
        rencana.anggaran_id = payload.anggaran_id
    if payload.nama_item is not None:
        rencana.nama_item = payload.nama_item
    if payload.volume is not None:
        if payload.volume <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Volume harus bernilai positif",
            )
        rencana.volume = payload.volume
    if payload.satuan is not None:
        rencana.satuan = payload.satuan
    if payload.harga_satuan is not None:
        if payload.harga_satuan <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Harga satuan harus bernilai positif",
            )
        rencana.harga_satuan = payload.harga_satuan

    rencana.subtotal = rencana.volume * rencana.harga_satuan
    db.commit()
    db.refresh(rencana)
    return rencana


@router.delete("/rencana/{rencana_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rencana(
    rencana_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    rencana = _get_rencana_or_404(db, rencana_id)
    db.delete(rencana)
    db.commit()


@router.get("/realisasi", response_model=List[schemas.RealisasiPengeluaranOut])
def list_realisasi(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user
    return db.query(models.RealisasiPengeluaran).order_by(models.RealisasiPengeluaran.id).all()


@router.post("/realisasi", response_model=schemas.RealisasiPengeluaranOut, status_code=status.HTTP_201_CREATED)
def create_realisasi(
    payload: schemas.RealisasiPengeluaranCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    anggaran = _get_anggaran_or_404(db, payload.anggaran_id)

    if payload.nominal <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nominal harus lebih dari nol",
        )

    total_realisasi = (
        db.query(func.coalesce(func.sum(models.RealisasiPengeluaran.nominal), 0))
        .filter(models.RealisasiPengeluaran.anggaran_id == payload.anggaran_id)
        .scalar()
    )
    sisa_anggaran = anggaran.pagu_anggaran - total_realisasi
    if payload.nominal > sisa_anggaran:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nominal pengeluaran melebihi sisa anggaran yang tersedia",
        )

    if payload.tanggal_transaksi > datetime.utcnow().date():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tanggal transaksi tidak boleh melebihi tanggal saat ini",
        )

    realisasi = models.RealisasiPengeluaran(
        tanggal_transaksi=payload.tanggal_transaksi,
        uraian=payload.uraian,
        nominal=payload.nominal,
        bukti_transaksi=payload.bukti_transaksi,
        keterangan=payload.keterangan,
        anggaran_id=payload.anggaran_id,
    )
    db.add(realisasi)
    db.commit()
    db.refresh(realisasi)
    return realisasi


@router.put("/realisasi/{realisasi_id}", response_model=schemas.RealisasiPengeluaranOut)
def update_realisasi(
    realisasi_id: int,
    payload: schemas.RealisasiPengeluaranUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    realisasi = _get_realisasi_or_404(db, realisasi_id)

    if payload.anggaran_id is not None:
        _get_anggaran_or_404(db, payload.anggaran_id)
        realisasi.anggaran_id = payload.anggaran_id
    if payload.tanggal_transaksi is not None:
        if payload.tanggal_transaksi > datetime.utcnow().date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tanggal transaksi tidak boleh melebihi tanggal saat ini",
            )
        realisasi.tanggal_transaksi = payload.tanggal_transaksi
    if payload.uraian is not None:
        realisasi.uraian = payload.uraian
    if payload.nominal is not None:
        if payload.nominal <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nominal harus lebih dari nol",
            )
        realisasi.nominal = payload.nominal
    if payload.bukti_transaksi is not None:
        realisasi.bukti_transaksi = payload.bukti_transaksi
    if payload.keterangan is not None:
        realisasi.keterangan = payload.keterangan

    db.commit()
    db.refresh(realisasi)
    return realisasi


@router.delete("/realisasi/{realisasi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_realisasi(
    realisasi_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_admin),
):
    realisasi = _get_realisasi_or_404(db, realisasi_id)
    db.delete(realisasi)
    db.commit()


@router.get("/dashboard/anggaran")
def dashboard_anggaran(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _ = current_user

    total_program = db.query(models.ProgramKerja).count()
    total_pagu = (
        db.query(func.coalesce(func.sum(models.Anggaran.pagu_anggaran), 0))
        .scalar()
    )
    total_realisasi = (
        db.query(func.coalesce(func.sum(models.RealisasiPengeluaran.nominal), 0))
        .scalar()
    )
    total_sisa = total_pagu - total_realisasi
    persen_penyerapan = round((total_realisasi / total_pagu * 100), 2) if total_pagu else 0

    return {
        "total_program": total_program,
        "total_pagu": total_pagu,
        "total_realisasi": total_realisasi,
        "total_sisa": total_sisa,
        "persen_penyerapan": persen_penyerapan,
    }
