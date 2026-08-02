from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models import (
    DOKUMEN_TIPE,
    GOLONGAN,
    HUB_KATEGORI,
    INSTRUKSI_DISPOSISI,
    JABATAN_DEWASA,
    PROGRAM_STATUS,
    ROLES,
    SIFAT_SURAT,
    STATUS_DISPOSISI,
    STATUS_PESANAN,
    STATUS_PRODUK,
    STATUS_REALISASI,
    STATUS_SURAT_KELUAR,
    STATUS_SURAT_MASUK,
    STATUS_TOKO,
    SUMBER_DANA,
    TINGKAT_WILAYAH,
)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    nama_lengkap: str
    role: str = "staff"
    tingkat_wilayah: Optional[str] = None
    wilayah_id: Optional[int] = None
    anggota_id: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    nama_lengkap: Optional[str] = None
    role: Optional[str] = None
    tingkat_wilayah: Optional[str] = None
    wilayah_id: Optional[int] = None
    anggota_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    username: str
    nama_lengkap: str
    role: str
    tingkat_wilayah: Optional[str]
    wilayah_id: Optional[int]
    anggota_id: Optional[int]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


# ---------- Wilayah ----------


class KwarcabCreate(BaseModel):
    nama: str
    kode_wilayah: str
    alamat_sekretariat: Optional[str] = None
    ketua: Optional[str] = None


class KwarcabUpdate(BaseModel):
    nama: Optional[str] = None
    kode_wilayah: Optional[str] = None
    alamat_sekretariat: Optional[str] = None
    ketua: Optional[str] = None


class KwarcabOut(BaseModel):
    id: int
    nama: str
    kode_wilayah: str
    alamat_sekretariat: Optional[str]
    ketua: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class KwaranCreate(BaseModel):
    nama: str
    kwarcab_id: int
    ketua: Optional[str] = None


class KwaranUpdate(BaseModel):
    nama: Optional[str] = None
    kwarcab_id: Optional[int] = None
    ketua: Optional[str] = None


class KwaranOut(BaseModel):
    id: int
    nama: str
    kwarcab_id: int
    ketua: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class GudepCreate(BaseModel):
    nomor_gudep: str
    nama_pangkalan: str
    jenis_pangkalan: str = "sekolah"
    kwaran_id: int
    pembina_gudep: Optional[str] = None
    alamat: Optional[str] = None


class GudepUpdate(BaseModel):
    nomor_gudep: Optional[str] = None
    nama_pangkalan: Optional[str] = None
    jenis_pangkalan: Optional[str] = None
    kwaran_id: Optional[int] = None
    pembina_gudep: Optional[str] = None
    alamat: Optional[str] = None


class GudepOut(BaseModel):
    id: int
    nomor_gudep: str
    nama_pangkalan: str
    jenis_pangkalan: str
    kwaran_id: int
    pembina_gudep: Optional[str]
    alamat: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Anggota ----------


class AnggotaCreate(BaseModel):
    nis_anggota: str
    nama_lengkap: str
    jenis_kelamin: str = "L"
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    golongan: str
    jabatan_dewasa: Optional[str] = None
    gudep_id: int
    nomor_hp: Optional[str] = None
    status_aktif: bool = True
    tanggal_bergabung: Optional[date] = None
    foto_url: Optional[str] = None


class AnggotaUpdate(BaseModel):
    nis_anggota: Optional[str] = None
    nama_lengkap: Optional[str] = None
    jenis_kelamin: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    golongan: Optional[str] = None
    jabatan_dewasa: Optional[str] = None
    gudep_id: Optional[int] = None
    nomor_hp: Optional[str] = None
    status_aktif: Optional[bool] = None
    tanggal_bergabung: Optional[date] = None
    foto_url: Optional[str] = None


class AnggotaOut(BaseModel):
    id: int
    nis_anggota: str
    nama_lengkap: str
    jenis_kelamin: str
    tempat_lahir: Optional[str]
    tanggal_lahir: Optional[date]
    golongan: str
    jabatan_dewasa: Optional[str]
    gudep_id: int
    nomor_hp: Optional[str]
    status_aktif: bool
    tanggal_bergabung: Optional[date]
    foto_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Program Kegiatan Internal Kwarda ----------


class BidangKwardaCreate(BaseModel):
    nama_bidang: str


class BidangKwardaUpdate(BaseModel):
    nama_bidang: Optional[str] = None


class BidangKwardaOut(BaseModel):
    id: int
    nama_bidang: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProgramKerjaCreate(BaseModel):
    judul: str
    bidang_id: int
    tahun: int
    deskripsi: Optional[str] = None
    target_capaian: Optional[str] = None
    penanggung_jawab: Optional[str] = None
    status: str = "rencana"


class ProgramKerjaUpdate(BaseModel):
    judul: Optional[str] = None
    bidang_id: Optional[int] = None
    tahun: Optional[int] = None
    deskripsi: Optional[str] = None
    target_capaian: Optional[str] = None
    penanggung_jawab: Optional[str] = None
    status: Optional[str] = None


class ProgramKerjaOut(BaseModel):
    id: int
    judul: str
    bidang_id: int
    tahun: int
    deskripsi: Optional[str]
    target_capaian: Optional[str]
    penanggung_jawab: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KegiatanCreate(BaseModel):
    program_kerja_id: Optional[int] = None
    judul: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: Optional[date] = None
    waktu: Optional[str] = None
    lokasi: Optional[str] = None
    penanggung_jawab: Optional[str] = None
    status: str = "rencana"
    untuk_publik: bool = False
    catatan_pelaksanaan: Optional[str] = None


class KegiatanUpdate(BaseModel):
    program_kerja_id: Optional[int] = None
    judul: Optional[str] = None
    deskripsi: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    waktu: Optional[str] = None
    lokasi: Optional[str] = None
    penanggung_jawab: Optional[str] = None
    status: Optional[str] = None
    untuk_publik: Optional[bool] = None
    catatan_pelaksanaan: Optional[str] = None


class KegiatanOut(BaseModel):
    id: int
    program_kerja_id: Optional[int]
    judul: str
    deskripsi: Optional[str]
    tanggal_mulai: date
    tanggal_selesai: Optional[date]
    waktu: Optional[str]
    lokasi: Optional[str]
    penanggung_jawab: Optional[str]
    status: str
    untuk_publik: bool
    catatan_pelaksanaan: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KegiatanDokumenOut(BaseModel):
    id: int
    kegiatan_id: int
    nama_file: str
    file_url: str
    tipe: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class KegiatanStatusUpdate(BaseModel):
    status: str


# ---------- Hub Kegiatan ----------


class HubKegiatanCreate(BaseModel):
    judul: str
    deskripsi: Optional[str] = None
    kategori: str
    tanggal_kegiatan: date
    lokasi: Optional[str] = None


class HubKegiatanUpdate(BaseModel):
    judul: Optional[str] = None
    deskripsi: Optional[str] = None
    kategori: Optional[str] = None
    tanggal_kegiatan: Optional[date] = None
    lokasi: Optional[str] = None


class HubKegiatanMediaOut(BaseModel):
    id: int
    hub_kegiatan_id: int
    tipe: str
    file_url: str
    urutan: int
    created_at: datetime

    model_config = {"from_attributes": True}


class HubKegiatanOut(BaseModel):
    id: int
    judul: str
    deskripsi: Optional[str]
    kategori: str
    tingkat_wilayah: str
    wilayah_id: int
    tanggal_kegiatan: date
    lokasi: Optional[str]
    status: str
    catatan_moderasi: Optional[str]
    submitted_by: int
    reviewed_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HubKegiatanReject(BaseModel):
    catatan_moderasi: str


# ---------- Sistem Persuratan Digital ----------


class KlasifikasiSuratCreate(BaseModel):
    kode: str
    nama_klasifikasi: str


class KlasifikasiSuratUpdate(BaseModel):
    kode: Optional[str] = None
    nama_klasifikasi: Optional[str] = None


class KlasifikasiSuratOut(BaseModel):
    id: int
    kode: str
    nama_klasifikasi: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SuratMasukCreate(BaseModel):
    nomor_surat_asal: Optional[str] = None
    tanggal_surat: date
    tanggal_diterima: date
    pengirim: str
    perihal: str
    klasifikasi_id: int
    sifat: str = "biasa"


class SuratMasukUpdate(BaseModel):
    nomor_surat_asal: Optional[str] = None
    tanggal_surat: Optional[date] = None
    tanggal_diterima: Optional[date] = None
    pengirim: Optional[str] = None
    perihal: Optional[str] = None
    klasifikasi_id: Optional[int] = None
    sifat: Optional[str] = None
    status: Optional[str] = None


class SuratMasukOut(BaseModel):
    id: int
    nomor_agenda: str
    nomor_surat_asal: Optional[str]
    tanggal_surat: date
    tanggal_diterima: date
    pengirim: str
    perihal: str
    klasifikasi_id: int
    sifat: str
    file_scan_url: Optional[str]
    status: str
    diinput_oleh: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SuratKeluarCreate(BaseModel):
    tanggal_surat: date
    tujuan: str
    perihal: str
    klasifikasi_id: int
    sifat: str = "biasa"
    isi_ringkas: Optional[str] = None


class SuratKeluarUpdate(BaseModel):
    tanggal_surat: Optional[date] = None
    tujuan: Optional[str] = None
    perihal: Optional[str] = None
    klasifikasi_id: Optional[int] = None
    sifat: Optional[str] = None
    isi_ringkas: Optional[str] = None


class SuratKeluarStatusUpdate(BaseModel):
    status: str


class SuratKeluarOut(BaseModel):
    id: int
    nomor_surat: Optional[str]
    tanggal_surat: date
    tujuan: str
    perihal: str
    klasifikasi_id: int
    sifat: str
    isi_ringkas: Optional[str]
    file_surat_url: Optional[str]
    status: str
    dibuat_oleh: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DisposisiCreate(BaseModel):
    kepada_user_id: int
    instruksi: str
    catatan: Optional[str] = None


class DisposisiStatusUpdate(BaseModel):
    catatan_penyelesaian: str


class DisposisiOut(BaseModel):
    id: int
    surat_masuk_id: int
    dari_user_id: int
    kepada_user_id: int
    instruksi: str
    catatan: Optional[str]
    status: str
    tanggal_disposisi: date
    tanggal_selesai: Optional[date]
    catatan_penyelesaian: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Sistem Perencanaan & Pelaporan ----------


class AnggaranProgramCreate(BaseModel):
    program_kerja_id: int
    tahun_anggaran: int
    jumlah_anggaran: int
    sumber_dana: str = "APBD"
    catatan: Optional[str] = None


class AnggaranProgramUpdate(BaseModel):
    tahun_anggaran: Optional[int] = None
    jumlah_anggaran: Optional[int] = None
    sumber_dana: Optional[str] = None
    catatan: Optional[str] = None


class AnggaranProgramOut(BaseModel):
    id: int
    program_kerja_id: int
    tahun_anggaran: int
    jumlah_anggaran: int
    sumber_dana: str
    catatan: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RealisasiAnggaranCreate(BaseModel):
    tanggal_realisasi: date
    jumlah_realisasi: int
    keterangan: str


class RealisasiAnggaranOut(BaseModel):
    id: int
    anggaran_program_id: int
    tanggal_realisasi: date
    jumlah_realisasi: int
    keterangan: str
    bukti_url: str
    status: str
    catatan_review: Optional[str]
    diinput_oleh: int
    direview_oleh: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RealisasiReview(BaseModel):
    status: str
    catatan_review: Optional[str] = None


class LaporanKegiatanCreate(BaseModel):
    kegiatan_id: int
    judul_laporan: str
    ringkasan_pelaksanaan: str
    jumlah_peserta: Optional[int] = None
    kendala: Optional[str] = None
    rekomendasi: Optional[str] = None
    tanggal_laporan: date


class LaporanKegiatanUpdate(BaseModel):
    judul_laporan: Optional[str] = None
    ringkasan_pelaksanaan: Optional[str] = None
    jumlah_peserta: Optional[int] = None
    kendala: Optional[str] = None
    rekomendasi: Optional[str] = None
    tanggal_laporan: Optional[date] = None


class LaporanKegiatanOut(BaseModel):
    id: int
    kegiatan_id: int
    judul_laporan: str
    ringkasan_pelaksanaan: str
    jumlah_peserta: Optional[int]
    kendala: Optional[str]
    rekomendasi: Optional[str]
    file_laporan_url: str
    tanggal_laporan: date
    dibuat_oleh: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Marketplace Pramuka ----------


class KategoriProdukCreate(BaseModel):
    nama_kategori: str


class KategoriProdukUpdate(BaseModel):
    nama_kategori: Optional[str] = None


class KategoriProdukOut(BaseModel):
    id: int
    nama_kategori: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokoCreate(BaseModel):
    nama_toko: str
    deskripsi: Optional[str] = None
    logo_url: Optional[str] = None
    nomor_rekening: str
    nama_bank: str
    nama_pemilik_rekening: str
    nomor_wa: Optional[str] = None
    alamat: Optional[str] = None


class TokoUpdate(BaseModel):
    nama_toko: Optional[str] = None
    deskripsi: Optional[str] = None
    logo_url: Optional[str] = None
    nomor_rekening: Optional[str] = None
    nama_bank: Optional[str] = None
    nama_pemilik_rekening: Optional[str] = None
    nomor_wa: Optional[str] = None
    alamat: Optional[str] = None


class TokoOut(BaseModel):
    id: int
    user_id: int
    nama_toko: str
    deskripsi: Optional[str]
    logo_url: Optional[str]
    nomor_rekening: str
    nama_bank: str
    nama_pemilik_rekening: str
    nomor_wa: Optional[str]
    alamat: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokoVerifikasi(BaseModel):
    status: str


class ProdukCreate(BaseModel):
    kategori_id: int
    nama_produk: str
    deskripsi: Optional[str] = None
    harga: int
    stok: int = 0


class ProdukUpdate(BaseModel):
    kategori_id: Optional[int] = None
    nama_produk: Optional[str] = None
    deskripsi: Optional[str] = None
    harga: Optional[int] = None
    stok: Optional[int] = None


class ProdukOut(BaseModel):
    id: int
    toko_id: int
    kategori_id: int
    nama_produk: str
    deskripsi: Optional[str]
    harga: int
    stok: int
    foto_url: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemPesananCreate(BaseModel):
    produk_id: int
    jumlah: int = 1


class PesananCreate(BaseModel):
    toko_id: int
    nama_pembeli: str
    kontak_pembeli: str
    alamat_pengiriman: str
    catatan_pembeli: Optional[str] = None
    items: list[ItemPesananCreate] = []


class PesananStatusUpdate(BaseModel):
    status: str
