from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base

ROLES = ("admin", "staff", "kontributor", "penjual")
TINGKAT_WILAYAH = ("kwarcab", "kwaran", "gudep")

GOLONGAN = ("siaga", "penggalang", "penegak", "pandega", "dewasa")
JABATAN_DEWASA = ("Pembina Pramuka", "Pelatih", "Andalan", "Lainnya")

PROGRAM_STATUS = ("rencana", "berjalan", "selesai", "dibatalkan")
DOKUMEN_TIPE = ("notulen", "absensi", "dokumentasi", "lainnya")
DOKUMEN_EXT_IZIN = (".pdf", ".jpg", ".jpeg", ".png", ".docx")
DOKUMEN_MAX_MB = 10

HUB_STATUS = ("pending", "approved", "rejected")
HUB_KATEGORI = ("berita", "dokumentasi", "agenda")
HUB_MEDIA_TIPE = ("foto", "video")
MEDIA_EXT_IZIN = (".jpg", ".jpeg", ".png", ".mp4", ".webm", ".mov")
MEDIA_MAX_MB = 50

SIFAT_SURAT = ("biasa", "penting", "segera", "rahasia")
STATUS_SURAT_MASUK = ("baru", "didisposisikan", "selesai", "diarsipkan")
STATUS_SURAT_KELUAR = ("draft", "menunggu_ttd", "terkirim")
INSTRUKSI_DISPOSISI = (
    "untuk_diketahui",
    "untuk_ditindaklanjuti",
    "untuk_disposisi_lanjut",
    "untuk_rapat",
    "lainnya",
)
STATUS_DISPOSISI = ("menunggu", "diproses", "selesai")
SURAT_EXT_IZIN = (".pdf", ".jpg", ".jpeg", ".png", ".docx")
SURAT_MAX_MB = 10

STATUS_REALISASI = ("diajukan", "disetujui", "ditolak")
SUMBER_DANA = ("APBD", "Swadaya", "Bantuan Pusat", "Lainnya")
BUKTI_EXT_IZIN = (".pdf", ".jpg", ".jpeg", ".png", ".docx")
BUKTI_MAX_MB = 10

STATUS_TOKO = ("pending", "aktif", "nonaktif")
STATUS_PRODUK = ("aktif", "nonaktif")
STATUS_PESANAN = (
    "menunggu_pembayaran",
    "menunggu_konfirmasi",
    "diproses",
    "dikirim",
    "selesai",
    "dibatalkan",
)
FOTO_EXT_IZIN = (".jpg", ".jpeg", ".png")
FOTO_MAX_MB = 5
BUKTI_TRANSFER_EXT_IZIN = (".pdf", ".jpg", ".jpeg", ".png")
BUKTI_TRANSFER_MAX_MB = 10


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    role = Column(String, nullable=False, default="staff")
    tingkat_wilayah = Column(String, nullable=True)
    wilayah_id = Column(Integer, nullable=True, index=True)
    anggota_id = Column(Integer, ForeignKey("anggota.id"), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    anggota = relationship("Anggota")


class Kwarcab(Base):
    __tablename__ = "kwarcab"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    kode_wilayah = Column(String, unique=True, nullable=False)
    alamat_sekretariat = Column(Text, nullable=True)
    ketua = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    kwaran = relationship("Kwaran", back_populates="kwarcab")


class Kwaran(Base):
    __tablename__ = "kwaran"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    kwarcab_id = Column(
        Integer, ForeignKey("kwarcab.id"), nullable=False, index=True
    )
    ketua = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    kwarcab = relationship("Kwarcab", back_populates="kwaran")
    gudep = relationship("Gudep", back_populates="kwaran")


class Gudep(Base):
    __tablename__ = "gudep"

    id = Column(Integer, primary_key=True, index=True)
    nomor_gudep = Column(String, nullable=False)
    nama_pangkalan = Column(String, nullable=False)
    jenis_pangkalan = Column(String, nullable=False, default="sekolah")
    kwaran_id = Column(
        Integer, ForeignKey("kwaran.id"), nullable=False, index=True
    )
    pembina_gudep = Column(String, nullable=True)
    alamat = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    kwaran = relationship("Kwaran", back_populates="gudep")
    anggota = relationship("Anggota", back_populates="gudep")


class Anggota(Base):
    __tablename__ = "anggota"

    id = Column(Integer, primary_key=True, index=True)
    nis_anggota = Column(String, unique=True, index=True, nullable=False)
    nama_lengkap = Column(String, nullable=False)
    jenis_kelamin = Column(String, nullable=False, default="L")
    tempat_lahir = Column(String, nullable=True)
    tanggal_lahir = Column(Date, nullable=True)
    golongan = Column(String, nullable=False, default="siaga")
    jabatan_dewasa = Column(String, nullable=True)
    gudep_id = Column(
        Integer, ForeignKey("gudep.id"), nullable=False, index=True
    )
    nomor_hp = Column(String, nullable=True)
    status_aktif = Column(Boolean, nullable=False, default=True)
    tanggal_bergabung = Column(Date, nullable=True)
    foto_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    gudep = relationship("Gudep", back_populates="anggota")


class BidangKwarda(Base):
    __tablename__ = "bidang_kwarda"

    id = Column(Integer, primary_key=True, index=True)
    nama_bidang = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    program_kerja = relationship("ProgramKerja", back_populates="bidang")


class ProgramKerja(Base):
    __tablename__ = "program_kerja"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, nullable=False)
    bidang_id = Column(
        Integer, ForeignKey("bidang_kwarda.id"), nullable=False, index=True
    )
    tahun = Column(Integer, nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    target_capaian = Column(Text, nullable=True)
    penanggung_jawab = Column(String, nullable=True)
    status = Column(String, nullable=False, default="rencana", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    bidang = relationship("BidangKwarda", back_populates="program_kerja")
    kegiatan = relationship("Kegiatan", back_populates="program_kerja")


class Kegiatan(Base):
    __tablename__ = "kegiatan"

    id = Column(Integer, primary_key=True, index=True)
    program_kerja_id = Column(
        Integer, ForeignKey("program_kerja.id"), nullable=True, index=True
    )
    judul = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=True)
    tanggal_mulai = Column(Date, nullable=False, index=True)
    tanggal_selesai = Column(Date, nullable=True)
    waktu = Column(String, nullable=True)
    lokasi = Column(String, nullable=True)
    penanggung_jawab = Column(String, nullable=True)
    status = Column(String, nullable=False, default="rencana", index=True)
    untuk_publik = Column(Boolean, nullable=False, default=False, index=True)
    catatan_pelaksanaan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    program_kerja = relationship("ProgramKerja", back_populates="kegiatan")
    dokumen = relationship(
        "KegiatanDokumen", back_populates="kegiatan", cascade="all, delete-orphan"
    )


class KegiatanDokumen(Base):
    __tablename__ = "kegiatan_dokumen"

    id = Column(Integer, primary_key=True, index=True)
    kegiatan_id = Column(
        Integer, ForeignKey("kegiatan.id"), nullable=False, index=True
    )
    nama_file = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    tipe = Column(String, nullable=False, default="lainnya")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    kegiatan = relationship("Kegiatan", back_populates="dokumen")


class HubKegiatan(Base):
    __tablename__ = "hub_kegiatan"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=True)
    kategori = Column(String, nullable=False, index=True)
    tingkat_wilayah = Column(String, nullable=False, index=True)
    wilayah_id = Column(Integer, nullable=False, index=True)
    tanggal_kegiatan = Column(Date, nullable=False)
    lokasi = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)
    catatan_moderasi = Column(Text, nullable=True)
    submitted_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    submitted_by_user = relationship(
        "User", foreign_keys=[submitted_by], backref="hub_postings"
    )
    reviewed_by_user = relationship(
        "User", foreign_keys=[reviewed_by], backref="hub_reviewed"
    )
    media = relationship(
        "HubKegiatanMedia",
        back_populates="hub_kegiatan",
        cascade="all, delete-orphan",
        order_by="HubKegiatanMedia.urutan",
    )


class HubKegiatanMedia(Base):
    __tablename__ = "hub_kegiatan_media"

    id = Column(Integer, primary_key=True, index=True)
    hub_kegiatan_id = Column(
        Integer, ForeignKey("hub_kegiatan.id"), nullable=False, index=True
    )
    tipe = Column(String, nullable=False, default="foto")
    file_url = Column(String, nullable=False)
    urutan = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    hub_kegiatan = relationship("HubKegiatan", back_populates="media")


class KlasifikasiSurat(Base):
    __tablename__ = "klasifikasi_surat"

    id = Column(Integer, primary_key=True, index=True)
    kode = Column(String, unique=True, nullable=False, index=True)
    nama_klasifikasi = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class SuratMasuk(Base):
    __tablename__ = "surat_masuk"

    id = Column(Integer, primary_key=True, index=True)
    nomor_agenda = Column(String, unique=True, nullable=False, index=True)
    nomor_surat_asal = Column(String, nullable=True)
    tanggal_surat = Column(Date, nullable=False)
    tanggal_diterima = Column(Date, nullable=False, index=True)
    pengirim = Column(String, nullable=False)
    perihal = Column(String, nullable=False)
    klasifikasi_id = Column(
        Integer, ForeignKey("klasifikasi_surat.id"), nullable=False, index=True
    )
    sifat = Column(String, nullable=False, default="biasa", index=True)
    file_scan_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="baru", index=True)
    diinput_oleh = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    klasifikasi = relationship("KlasifikasiSurat", backref="surat_masuk_list")
    diinput_oleh_user = relationship(
        "User", foreign_keys=[diinput_oleh], backref="surat_masuk_input"
    )
    disposisi = relationship(
        "Disposisi",
        back_populates="surat_masuk",
        cascade="all, delete-orphan",
        order_by="Disposisi.tanggal_disposisi.asc(), Disposisi.id.asc()",
    )


class SuratKeluar(Base):
    __tablename__ = "surat_keluar"

    id = Column(Integer, primary_key=True, index=True)
    nomor_surat = Column(String, unique=True, nullable=True, index=True)
    tanggal_surat = Column(Date, nullable=False)
    tujuan = Column(String, nullable=False)
    perihal = Column(String, nullable=False)
    klasifikasi_id = Column(
        Integer, ForeignKey("klasifikasi_surat.id"), nullable=False, index=True
    )
    sifat = Column(String, nullable=False, default="biasa", index=True)
    isi_ringkas = Column(Text, nullable=True)
    file_surat_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft", index=True)
    dibuat_oleh = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    klasifikasi = relationship("KlasifikasiSurat", backref="surat_keluar_list")
    dibuat_oleh_user = relationship(
        "User", foreign_keys=[dibuat_oleh], backref="surat_keluar_buat"
    )


class Disposisi(Base):
    __tablename__ = "disposisi"

    id = Column(Integer, primary_key=True, index=True)
    surat_masuk_id = Column(
        Integer, ForeignKey("surat_masuk.id"), nullable=False, index=True
    )
    dari_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    kepada_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    instruksi = Column(String, nullable=False)
    catatan = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="menunggu", index=True)
    tanggal_disposisi = Column(Date, nullable=False)
    tanggal_selesai = Column(Date, nullable=True)
    catatan_penyelesaian = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    surat_masuk = relationship("SuratMasuk", back_populates="disposisi")
    dari_user = relationship(
        "User", foreign_keys=[dari_user_id], backref="disposisi_dari"
    )
    kepada_user = relationship(
        "User", foreign_keys=[kepada_user_id], backref="disposisi_kepada"
    )


class PersuratanCounter(Base):
    __tablename__ = "persuratan_counter"

    id = Column(Integer, primary_key=True, index=True)
    jenis = Column(String, nullable=False)  # "masuk" | "keluar"
    tahun = Column(Integer, nullable=False)
    urutan = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("jenis", "tahun", name="uq_persuratan_counter_jenis_tahun"),
    )


class AnggaranProgram(Base):
    __tablename__ = "anggaran_program"

    id = Column(Integer, primary_key=True, index=True)
    program_kerja_id = Column(
        Integer, ForeignKey("program_kerja.id"), nullable=False, index=True
    )
    tahun_anggaran = Column(Integer, nullable=False, index=True)
    jumlah_anggaran = Column(Integer, nullable=False)
    sumber_dana = Column(String, nullable=False, default="APBD")
    catatan = Column(Text, nullable=True)
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "program_kerja_id", "tahun_anggaran", name="uq_anggaran_program_pk_tahun"
        ),
    )

    program_kerja = relationship("ProgramKerja", backref="anggaran_program")
    created_by_user = relationship(
        "User", foreign_keys=[created_by], backref="anggaran_dibuat"
    )
    realisasi = relationship(
        "RealisasiAnggaran",
        back_populates="anggaran_program",
        cascade="all, delete-orphan",
    )


class RealisasiAnggaran(Base):
    __tablename__ = "realisasi_anggaran"

    id = Column(Integer, primary_key=True, index=True)
    anggaran_program_id = Column(
        Integer, ForeignKey("anggaran_program.id"), nullable=False, index=True
    )
    tanggal_realisasi = Column(Date, nullable=False, index=True)
    jumlah_realisasi = Column(Integer, nullable=False)
    keterangan = Column(Text, nullable=False)
    bukti_url = Column(String, nullable=False)
    status = Column(String, nullable=False, default="diajukan", index=True)
    catatan_review = Column(Text, nullable=True)
    diinput_oleh = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    direview_oleh = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    anggaran_program = relationship("AnggaranProgram", back_populates="realisasi")
    diinput_oleh_user = relationship(
        "User", foreign_keys=[diinput_oleh], backref="realisasi_diinput"
    )
    direview_oleh_user = relationship(
        "User", foreign_keys=[direview_oleh], backref="realisasi_direview"
    )


class LaporanKegiatan(Base):
    __tablename__ = "laporan_kegiatan"

    id = Column(Integer, primary_key=True, index=True)
    kegiatan_id = Column(
        Integer, ForeignKey("kegiatan.id"), nullable=False, index=True
    )
    judul_laporan = Column(String, nullable=False)
    ringkasan_pelaksanaan = Column(Text, nullable=False)
    jumlah_peserta = Column(Integer, nullable=True)
    kendala = Column(Text, nullable=True)
    rekomendasi = Column(Text, nullable=True)
    file_laporan_url = Column(String, nullable=False)
    tanggal_laporan = Column(Date, nullable=False)
    dibuat_oleh = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    kegiatan = relationship("Kegiatan", backref="laporan_kegiatan")
    dibuat_oleh_user = relationship(
        "User", foreign_keys=[dibuat_oleh], backref="laporan_dibuat"
    )


class Toko(Base):
    __tablename__ = "toko"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    nama_toko = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    nomor_rekening = Column(String, nullable=False)
    nama_bank = Column(String, nullable=False)
    nama_pemilik_rekening = Column(String, nullable=False)
    nomor_wa = Column(String, nullable=True)
    alamat = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", backref="toko")
    produk = relationship(
        "Produk", back_populates="toko", cascade="all, delete-orphan"
    )
    pesanan = relationship("Pesanan", back_populates="toko")


class KategoriProduk(Base):
    __tablename__ = "kategori_produk"

    id = Column(Integer, primary_key=True, index=True)
    nama_kategori = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    produk = relationship("Produk", back_populates="kategori")


class Produk(Base):
    __tablename__ = "produk"

    id = Column(Integer, primary_key=True, index=True)
    toko_id = Column(Integer, ForeignKey("toko.id"), nullable=False, index=True)
    kategori_id = Column(
        Integer, ForeignKey("kategori_produk.id"), nullable=False, index=True
    )
    nama_produk = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=True)
    harga = Column(Integer, nullable=False)
    stok = Column(Integer, nullable=False, default=0)
    foto_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="aktif", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    toko = relationship("Toko", back_populates="produk")
    kategori = relationship("KategoriProduk", back_populates="produk")
    items = relationship("ItemPesanan", back_populates="produk")


class Pesanan(Base):
    __tablename__ = "pesanan"

    id = Column(Integer, primary_key=True, index=True)
    nomor_pesanan = Column(String, unique=True, nullable=False, index=True)
    pembeli_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    toko_id = Column(Integer, ForeignKey("toko.id"), nullable=False, index=True)
    nama_pembeli = Column(String, nullable=False)
    kontak_pembeli = Column(String, nullable=False)
    alamat_pengiriman = Column(Text, nullable=False)
    total_harga = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="menunggu_pembayaran", index=True)
    bukti_transfer_url = Column(String, nullable=True)
    catatan_pembeli = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    toko = relationship("Toko", back_populates="pesanan")
    pembeli_user = relationship("User", backref="pesanan_dibeli")
    items = relationship(
        "ItemPesanan",
        back_populates="pesanan",
        cascade="all, delete-orphan",
        order_by="ItemPesanan.id",
    )


class ItemPesanan(Base):
    __tablename__ = "item_pesanan"

    id = Column(Integer, primary_key=True, index=True)
    pesanan_id = Column(
        Integer, ForeignKey("pesanan.id"), nullable=False, index=True
    )
    produk_id = Column(Integer, ForeignKey("produk.id"), nullable=True, index=True)
    nama_produk_saat_beli = Column(String, nullable=False)
    harga_saat_beli = Column(Integer, nullable=False)
    jumlah = Column(Integer, nullable=False, default=1)
    subtotal = Column(Integer, nullable=False, default=0)

    pesanan = relationship("Pesanan", back_populates="items")
    produk = relationship("Produk", back_populates="items")


class PesananCounter(Base):
    __tablename__ = "pesanan_counter"

    id = Column(Integer, primary_key=True, index=True)
    tahun = Column(Integer, nullable=False)
    bulan = Column(Integer, nullable=False)
    urutan = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("tahun", "bulan", name="uq_pesanan_counter_tahun_bulan"),
    )
