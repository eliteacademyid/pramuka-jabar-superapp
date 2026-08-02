from datetime import date, timedelta

from app import models
from app.database import SessionLocal

# Contoh data: 2 kwarcab, beberapa kwaran, gudep, dan anggota
# supaya form cascading & rekap statistik langsung bisa dicoba.

DATA = {
    "kwarcab": [
        {
            "nama": "Kabupaten Bandung",
            "kode_wilayah": "3204",
            "alamat_sekretariat": "Jl. Merdeka No. 10, Soreang, Bandung",
            "ketua": "Kak. Asep Sunandar",
        },
        {
            "nama": "Kota Bandung",
            "kode_wilayah": "3273",
            "alamat_sekretariat": "Jl. Asia Afrika No. 25, Bandung",
            "ketua": "Kak. Dewi Anggraeni",
        },
    ],
    "kwaran": [
        {"nama": "Soreang", "kwarcab_nama": "Kabupaten Bandung", "ketua": "Kak. Budi"},
        {"nama": "Banjar", "kwarcab_nama": "Kabupaten Bandung", "ketua": "Kak. Sari"},
        {"nama": "Coblong", "kwarcab_nama": "Kota Bandung", "ketua": "Kak. Rina"},
    ],
    "gudep": [
        {"nomor_gudep": "04.001", "nama_pangkalan": "SMA Negeri 1 Soreang", "jenis_pangkalan": "sekolah", "kwaran_nama": "Soreang", "pembina_gudep": "Kak. Hendra", "alamat": "Jl. Pendidikan No. 1, Soreang"},
        {"nomor_gudep": "04.005", "nama_pangkalan": "MTs Al-Hidayah", "jenis_pangkalan": "sekolah", "kwaran_nama": "Banjar", "pembina_gudep": "Kak. Fitri", "alamat": "Jl. Raya Banjar No. 8"},
        {"nomor_gudep": "04.010", "nama_pangkalan": "Komunitas Pramuka Kreatif", "jenis_pangkalan": "komunitas", "kwaran_nama": "Coblong", "pembina_gudep": "Kak. Rudi", "alamat": "Jl. Dago No. 12, Bandung"},
    ],
    "anggota": [
        {"nis": "3204.001", "nama": "Ahmad Fauzi", "jk": "L", "golongan": "penggalang", "gudep_nomor": "04.001", "tanggal_lahir": date(2012, 5, 12), "hp": "0812-0001"},
        {"nis": "3204.002", "nama": "Siti Nurhaliza", "jk": "P", "golongan": "penggalang", "gudep_nomor": "04.001", "tanggal_lahir": date(2012, 8, 3), "hp": "0812-0002"},
        {"nis": "3204.003", "nama": "Rizky Pratama", "jk": "L", "golongan": "penegak", "gudep_nomor": "04.005", "tanggal_lahir": date(2008, 1, 20), "hp": "0812-0003"},
        {"nis": "3204.004", "nama": "Nadia Putri", "jk": "P", "golongan": "pandega", "gudep_nomor": "04.010", "tanggal_lahir": date(2004, 11, 15), "hp": "0812-0004"},
        {"nis": "3204.005", "nama": "Bambang Sutrisno", "jk": "L", "golongan": "dewasa", "jabatan": "Pembina Pramuka", "gudep_nomor": "04.010", "tanggal_lahir": date(1985, 3, 9), "hp": "0812-0005"},
        {"nis": "3204.006", "nama": "Citra Ayu", "jk": "P", "golongan": "siaga", "gudep_nomor": "04.001", "tanggal_lahir": date(2016, 2, 28), "hp": "0812-0006"},
    ],
}


def seed_dummy_data():
    db = SessionLocal()
    try:
        if db.query(models.Kwarcab).count() > 0:
            print("Data wilayah sudah ada, lewati seeding dummy.")
            return

        kwarcab_map = {}
        for item in DATA["kwarcab"]:
            kwarcab = models.Kwarcab(**item)
            db.add(kwarcab)
            db.flush()
            kwarcab_map[kwarcab.nama] = kwarcab

        kwaran_map = {}
        for item in DATA["kwaran"]:
            kwaran = models.Kwaran(
                nama=item["nama"],
                kwarcab_id=kwarcab_map[item["kwarcab_nama"]].id,
                ketua=item["ketua"],
            )
            db.add(kwaran)
            db.flush()
            kwaran_map[kwaran.nama] = kwaran

        gudep_map = {}
        for item in DATA["gudep"]:
            gudep = models.Gudep(
                nomor_gudep=item["nomor_gudep"],
                nama_pangkalan=item["nama_pangkalan"],
                jenis_pangkalan=item["jenis_pangkalan"],
                kwaran_id=kwaran_map[item["kwaran_nama"]].id,
                pembina_gudep=item["pembina_gudep"],
                alamat=item["alamat"],
            )
            db.add(gudep)
            db.flush()
            gudep_map[gudep.nomor_gudep] = gudep

        for item in DATA["anggota"]:
            db.add(
                models.Anggota(
                    nis_anggota=item["nis"],
                    nama_lengkap=item["nama"],
                    jenis_kelamin=item["jk"],
                    golongan=item["golongan"],
                    jabatan_dewasa=item.get("jabatan"),
                    gudep_id=gudep_map[item["gudep_nomor"]].id,
                    tanggal_lahir=item["tanggal_lahir"],
                    nomor_hp=item["hp"],
                    status_aktif=True,
                    tanggal_bergabung=date.today() - timedelta(days=30),
                )
            )

        db.commit()
        print("Seeding dummy berhasil: 2 kwarcab, 3 kwaran, 3 gudep, 6 anggota.")
    finally:
        db.close()


def seed_kegiatan_internal():
    db = SessionLocal()
    try:
        if db.query(models.BidangKwarda).count() > 0:
            print("Data kegiatan internal sudah ada, lewati seeding.")
            return

        nama_bidang = [
            "Bidang Pembinaan Anggota Muda",
            "Bidang Organisasi",
            "Bidang Abdimas",
            "Bidang Pembinaan Anggota Dewasa",
            "Bidang Komunikasi & Informasi",
        ]
        bidang_map = {}
        for nama in nama_bidang:
            obj = models.BidangKwarda(nama_bidang=nama)
            db.add(obj)
            db.flush()
            bidang_map[nama] = obj.id

        program_rows = [
            {
                "judul": "Raimuna Daerah Jabar 2026",
                "bidang": "Bidang Pembinaan Anggota Muda",
                "tahun": 2026,
                "penanggung_jawab": "Kak. Dewi Anggraeni",
                "status": "berjalan",
            },
            {
                "judul": "Sistem Informasi Anggota (SIA)",
                "bidang": "Bidang Komunikasi & Informasi",
                "tahun": 2026,
                "penanggung_jawab": "Kak. Asep Sunandar",
                "status": "berjalan",
            },
            {
                "judul": "Pelatihan Pembina Mahir Tingkat Dasar",
                "bidang": "Bidang Pembinaan Anggota Dewasa",
                "tahun": 2026,
                "penanggung_jawab": "Kak. Bambang Sutrisno",
                "status": "rencana",
            },
            {
                "judul": "Peningkatan Kualitas Organisasi Kwarcab",
                "bidang": "Bidang Organisasi",
                "tahun": 2025,
                "penanggung_jawab": "Kak. Rina Yuliana",
                "status": "selesai",
            },
        ]
        program_map = {}
        for p in program_rows:
            obj = models.ProgramKerja(
                judul=p["judul"],
                bidang_id=bidang_map[p["bidang"]],
                tahun=p["tahun"],
                penanggung_jawab=p["penanggung_jawab"],
                status=p["status"],
            )
            db.add(obj)
            db.flush()
            program_map[obj.judul] = obj.id

        hari_ini = date.today()
        kegiatan_rows = [
            {
                "judul": "Rapat Persiapan Raimuna",
                "program": "Raimuna Daerah Jabar 2026",
                "tanggal_mulai": hari_ini + timedelta(days=3),
                "tanggal_selesai": hari_ini + timedelta(days=3),
                "waktu": "09.00 - 12.00 WIB",
                "lokasi": "Aula Kwarda Jabar",
                "penanggung_jawab": "Kak. Dewi Anggraeni",
                "status": "rencana",
            },
            {
                "judul": "Sosialisasi Aplikasi SIA ke Kwarcab",
                "program": "Sistem Informasi Anggota (SIA)",
                "tanggal_mulai": hari_ini + timedelta(days=10),
                "tanggal_selesai": hari_ini + timedelta(days=11),
                "waktu": "08.00 - 15.00 WIB",
                "lokasi": "Hotel Grand Tjokro, Bandung",
                "penanggung_jawab": "Kak. Asep Sunandar",
                "status": "rencana",
            },
            {
                "judul": "Musyawarah Bidang Organisasi",
                "program": "Peningkatan Kualitas Organisasi Kwarcab",
                "tanggal_mulai": hari_ini - timedelta(days=30),
                "tanggal_selesai": hari_ini - timedelta(days=30),
                "waktu": "09.00 - 16.00 WIB",
                "lokasi": "Gedung Kwarcab Kab. Bandung",
                "penanggung_jawab": "Kak. Rina Yuliana",
                "status": "selesai",
                "catatan_pelaksanaan": "Dihadiri 27 pengurus, menghasilkan 5 rekomendasi program tahunan.",
            },
            {
                "judul": "Pelatihan Pembina Mahir (batch 1)",
                "program": "Pelatihan Pembina Mahir Tingkat Dasar",
                "tanggal_mulai": hari_ini + timedelta(days=20),
                "tanggal_selesai": hari_ini + timedelta(days=23),
                "waktu": "08.00 - 17.00 WIB",
                "lokasi": "Pondok Pramuka Cibubur",
                "penanggung_jawab": "Kak. Bambang Sutrisno",
                "status": "rencana",
            },
            {
                "judul": "Hari Ulang Tahun Pramuka",
                "program": None,
                "tanggal_mulai": hari_ini + timedelta(days=40),
                "tanggal_selesai": hari_ini + timedelta(days=40),
                "waktu": "06.00 - 17.00 WIB",
                "lokasi": "Lapangan Gasibu, Bandung",
                "penanggung_jawab": "Kak. Ketua Kwarda",
                "status": "rencana",
            },
        ]
        for k in kegiatan_rows:
            db.add(
                models.Kegiatan(
                    program_kerja_id=program_map.get(k["program"]),
                    judul=k["judul"],
                    tanggal_mulai=k["tanggal_mulai"],
                    tanggal_selesai=k["tanggal_selesai"],
                    waktu=k["waktu"],
                    lokasi=k["lokasi"],
                    penanggung_jawab=k["penanggung_jawab"],
                    status=k["status"],
                    catatan_pelaksanaan=k.get("catatan_pelaksanaan"),
                )
            )

        db.commit()
        print(
            "Seeding kegiatan internal berhasil: 5 bidang, 4 program kerja, 5 kegiatan."
        )
    finally:
        db.close()


def seed_kontributor():
    from app import auth

    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.username == "kontributor").first()
        if existing:
            print("Akun kontributor sudah ada, lewati.")
            return

        kwaran = db.query(models.Kwaran).filter(models.Kwaran.nama == "Coblong").first()
        if not kwaran:
            kwaran = db.query(models.Kwaran).first()
        if not kwaran:
            print("Tidak ada data kwaran, lewati seed kontributor.")
            return

        user = models.User(
            username="kontributor",
            hashed_password=auth.hash_password("kontributor123"),
            nama_lengkap="Kak. Kontributor Kwaran Coblong",
            role="kontributor",
            tingkat_wilayah="kwaran",
            wilayah_id=kwaran.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Akun kontributor dibuat: username='kontributor', terhubung ke kwaran '{kwaran.nama}' (id={kwaran.id}).")
    finally:
        db.close()


def seed_persuratan():
    from datetime import timedelta

    db = SessionLocal()
    try:
        if db.query(models.KlasifikasiSurat).count() > 0:
            print("Data persuratan sudah ada, lewati seeding.")
            return

        klasifikasi_rows = [
            ("001", "Umum"),
            ("002", "Kepegawaian"),
            ("003", "Keuangan"),
            ("004", "Organisasi"),
            ("005", "Sarana & Prasarana"),
            ("006", "Pendidikan & Latihan"),
            ("007", "Komunikasi & Informasi"),
        ]
        for kode, nama in klasifikasi_rows:
            db.add(models.KlasifikasiSurat(kode=kode, nama_klasifikasi=nama))
        db.flush()

        staf_rows = [
            ("staf1", "Kak. Siti Staf Sekretariat"),
            ("staf2", "Kak. Budi Staf Kabid Organisasi"),
        ]
        from app import auth

        for username, nama in staf_rows:
            if db.query(models.User).filter(models.User.username == username).first():
                continue
            db.add(
                models.User(
                    username=username,
                    hashed_password=auth.hash_password("staf12345"),
                    nama_lengkap=nama,
                    role="staff",
                    is_active=True,
                )
            )
        db.flush()

        admin = db.query(models.User).filter(models.User.username == "admin").first()
        diinput = admin.id if admin else None

        umum = (
            db.query(models.KlasifikasiSurat)
            .filter(models.KlasifikasiSurat.kode == "001")
            .first()
        )
        kepeg = (
            db.query(models.KlasifikasiSurat)
            .filter(models.KlasifikasiSurat.kode == "002")
            .first()
        )
        keuangan = (
            db.query(models.KlasifikasiSurat)
            .filter(models.KlasifikasiSurat.kode == "003")
            .first()
        )

        hari_ini = date.today()
        surat_rows = [
            {
                "nomor_agenda": None,
                "nomor_surat_asal": "005/PAN-RAI/VII/2026",
                "tanggal_surat": hari_ini - timedelta(days=2),
                "tanggal_diterima": hari_ini - timedelta(days=1),
                "pengirim": "Panitia Raimuna Daerah",
                "perihal": "Undangan Rapat Koordinasi Panitia Raimuna",
                "klasifikasi": umum,
                "sifat": "biasa",
                "status": "baru",
            },
            {
                "nomor_agenda": None,
                "nomor_surat_asal": "B-014/Sekretariat/2026",
                "tanggal_surat": hari_ini - timedelta(days=5),
                "tanggal_diterima": hari_ini - timedelta(days=4),
                "pengirim": "Sekretariat Kwarcab Kota Bandung",
                "perihal": "Permohonan Data Kepegawaian Anggota Dewasa",
                "klasifikasi": kepeg,
                "sifat": "segera",
                "status": "baru",
            },
            {
                "nomor_agenda": None,
                "nomor_surat_asal": "012/Keuangan/Pusat/2026",
                "tanggal_surat": hari_ini - timedelta(days=8),
                "tanggal_diterima": hari_ini - timedelta(days=7),
                "pengirim": "Bendahara Kwartir Nasional",
                "perihal": "Pencairan Dana Bantuan Kegiatan",
                "klasifikasi": keuangan,
                "sifat": "penting",
                "status": "baru",
            },
        ]

        counter_map = {}
        for i, item in enumerate(surat_rows, start=1):
            tahun = item["tanggal_diterima"].year
            urutan = counter_map.get(tahun, 0) + 1
            counter_map[tahun] = urutan
            sm = models.SuratMasuk(
                nomor_agenda=f"AGD/{urutan}/{tahun}",
                nomor_surat_asal=item["nomor_surat_asal"],
                tanggal_surat=item["tanggal_surat"],
                tanggal_diterima=item["tanggal_diterima"],
                pengirim=item["pengirim"],
                perihal=item["perihal"],
                klasifikasi_id=item["klasifikasi"].id,
                sifat=item["sifat"],
                status=item["status"],
                diinput_oleh=diinput,
            )
            db.add(sm)

        db.commit()
        print(
            "Seeding persuratan berhasil: 7 klasifikasi, 2 user staf, 3 surat masuk."
        )
    finally:
        db.close()


def seed_pelaporan():
    from pathlib import Path

    from app.config import UPLOAD_DIR

    db = SessionLocal()
    try:
        if db.query(models.AnggaranProgram).count() > 0:
            print("Data perencanaan & pelaporan sudah ada, lewati seeding.")
            return

        admin = db.query(models.User).filter(models.User.username == "admin").first()
        staf1 = db.query(models.User).filter(models.User.username == "staf1").first()
        user = admin or staf1 or db.query(models.User).first()
        if not user:
            print("Tidak ada user, lewati seed pelaporan.")
            return

        Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        upload_dir = Path(UPLOAD_DIR)
        bukti_seed = upload_dir / "seed_bukti_realisasi.txt"
        laporan_seed = upload_dir / "seed_laporan_kegiatan.txt"
        if not bukti_seed.exists():
            bukti_seed.write_text(
                "BUKTI SEED - realisasi anggaran (kwitansi/nota placeholder)\n"
                "Dibuat otomatis oleh seed_pelaporan().\n",
                encoding="utf-8",
            )
        if not laporan_seed.exists():
            laporan_seed.write_text(
                "LAPORAN SEED - laporan pelaksanaan kegiatan (placeholder)\n"
                "Dibuat otomatis oleh seed_pelaporan().\n",
                encoding="utf-8",
            )
        bukti_url = "/uploads/seed_bukti_realisasi.txt"
        laporan_url = "/uploads/seed_laporan_kegiatan.txt"

        program_map = {
            p.judul: p for p in db.query(models.ProgramKerja).all()
        }

        anggaran_rows = [
            {
                "program": "Raimuna Daerah Jabar 2026",
                "tahun": 2026,
                "jumlah": 150_000_000,
                "sumber": "APBD",
                "catatan": "Anggaran utama penyelenggaraan Raimuna Daerah.",
            },
            {
                "program": "Sistem Informasi Anggota (SIA)",
                "tahun": 2026,
                "jumlah": 100_000_000,
                "sumber": "Bantuan Pusat",
                "catatan": "Dukungan pengembangan & operasional SIA.",
            },
            {
                "program": "Pelatihan Pembina Mahir Tingkat Dasar",
                "tahun": 2026,
                "jumlah": 80_000_000,
                "sumber": "Swadaya",
                "catatan": "Swadaya dari iuran peserta & donatur.",
            },
        ]

        realisasi_seed = [
            {
                "program": "Raimuna Daerah Jabar 2026",
                "tanggal": date(2026, 6, 10),
                "jumlah": 50_000_000,
                "keterangan": "Konsumsi & akomodasi peserta (hotel & katering)",
                "status": "disetujui",
                "catatan_review": None,
            },
            {
                "program": "Raimuna Daerah Jabar 2026",
                "tanggal": date(2026, 7, 5),
                "jumlah": 25_000_000,
                "keterangan": "Transportasi panitia & narasumber",
                "status": "disetujui",
                "catatan_review": None,
            },
            {
                "program": "Raimuna Daerah Jabar 2026",
                "tanggal": date(2026, 7, 20),
                "jumlah": 15_000_000,
                "keterangan": "Cetak spanduk, umbul-umbul, dan ATK",
                "status": "diajukan",
                "catatan_review": None,
            },
            {
                "program": "Sistem Informasi Anggota (SIA)",
                "tanggal": date(2026, 5, 15),
                "jumlah": 30_000_000,
                "keterangan": "Pengembangan fitur aplikasi SIA",
                "status": "disetujui",
                "catatan_review": None,
            },
            {
                "program": "Sistem Informasi Anggota (SIA)",
                "tanggal": date(2026, 6, 28),
                "jumlah": 10_000_000,
                "keterangan": "Pembelian server tambahan",
                "status": "ditolak",
                "catatan_review": "Belum ada kebutuhan server tambahan, gunakan server existing.",
            },
            {
                "program": "Sistem Informasi Anggota (SIA)",
                "tanggal": date(2026, 7, 18),
                "jumlah": 20_000_000,
                "keterangan": "Hosting & domain tahunan",
                "status": "diajukan",
                "catatan_review": None,
            },
        ]

        ap_map = {}
        for item in anggaran_rows:
            program = program_map.get(item["program"])
            if not program:
                continue
            ap = models.AnggaranProgram(
                program_kerja_id=program.id,
                tahun_anggaran=item["tahun"],
                jumlah_anggaran=item["jumlah"],
                sumber_dana=item["sumber"],
                catatan=item["catatan"],
                created_by=user.id,
            )
            db.add(ap)
            db.flush()
            ap_map[item["program"]] = ap

        for item in realisasi_seed:
            ap = ap_map.get(item["program"])
            if not ap:
                continue
            db.add(
                models.RealisasiAnggaran(
                    anggaran_program_id=ap.id,
                    tanggal_realisasi=item["tanggal"],
                    jumlah_realisasi=item["jumlah"],
                    keterangan=item["keterangan"],
                    bukti_url=bukti_url,
                    status=item["status"],
                    catatan_review=item["catatan_review"],
                    diinput_oleh=user.id,
                    direview_oleh=user.id
                    if item["status"] in ("disetujui", "ditolak")
                    else None,
                )
            )

        musybid = db.query(models.Kegiatan).filter(
            models.Kegiatan.judul == "Musyawarah Bidang Organisasi"
        ).first()
        if musybid and musybid.status == "selesai":
            db.add(
                models.LaporanKegiatan(
                    kegiatan_id=musybid.id,
                    judul_laporan="Laporan Pelaksanaan Musyawarah Bidang Organisasi",
                    ringkasan_pelaksanaan=(
                        "Musyawarah dilaksanakan di Gedung Kwarcab Kab. Bandung, "
                        "dihadiri 27 pengurus, menghasilkan 5 rekomendasi program tahunan."
                    ),
                    jumlah_peserta=27,
                    kendala="Beberapa kwarcab terlambat mengirim delegasi.",
                    rekomendasi="Perlu jadwal lebih awal dan undangan digital.",
                    file_laporan_url=laporan_url,
                    tanggal_laporan=musybid.tanggal_mulai,
                    dibuat_oleh=user.id,
                )
            )

        db.commit()
        print(
            "Seeding perencanaan & pelaporan berhasil: 3 alokasi anggaran, "
            "6 realisasi (2 diajukan, 3 disetujui, 1 ditolak), 1 laporan kegiatan."
        )
    finally:
        db.close()


def seed_marketplace():
    import base64
    from datetime import datetime, timedelta
    from pathlib import Path

    from app import auth
    from app.config import UPLOAD_DIR
    from app.routers.marketplace import _buat_nomor_pesanan

    db = SessionLocal()
    try:
        if db.query(models.Toko).count() > 0:
            print("Data marketplace sudah ada, lewati seeding.")
            return

        Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        upload_dir = Path(UPLOAD_DIR)
        foto_seed = upload_dir / "seed_foto_produk.png"
        if not foto_seed.exists():
            foto_seed.write_bytes(
                base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
                )
            )
        bukti_seed = upload_dir / "seed_bukti_transfer.txt"
        if not bukti_seed.exists():
            bukti_seed.write_text(
                "BUKTI SEED - bukti transfer marketplace (placeholder)\n"
                "Dibuat otomatis oleh seed_marketplace().\n",
                encoding="utf-8",
            )
        foto_url = "/uploads/seed_foto_produk.png"
        bukti_url = "/uploads/seed_bukti_transfer.txt"

        anggota_map = {a.nama_lengkap: a for a in db.query(models.Anggota).all()}

        penjual_rows = [
            {
                "username": "penjual1",
                "password": "penjual12345",
                "nama_lengkap": "Kak. Bambang Sutrisno",
                "anggota": "Bambang Sutrisno",
            },
            {
                "username": "penjual2",
                "password": "penjual12345",
                "nama_lengkap": "Kak. Nadia Putri",
                "anggota": "Nadia Putri",
            },
            {
                "username": "penjual3",
                "password": "penjual12345",
                "nama_lengkap": "Kak. Rizky Pratama",
                "anggota": "Rizky Pratama",
            },
        ]
        penjual_map = {}
        for p in penjual_rows:
            user = (
                db.query(models.User)
                .filter(models.User.username == p["username"])
                .first()
            )
            if not user:
                user = models.User(
                    username=p["username"],
                    hashed_password=auth.hash_password(p["password"]),
                    nama_lengkap=p["nama_lengkap"],
                    role="penjual",
                    is_active=True,
                    anggota_id=anggota_map[p["anggota"]].id
                    if p["anggota"] in anggota_map
                    else None,
                )
                db.add(user)
                db.flush()
            penjual_map[p["username"]] = user

        kategori_rows = [
            "Seragam & Atribut",
            "Kerajinan Tangan",
            "Makanan Olahan",
            "Alat Kemah",
        ]
        kategori_map = {}
        for nama in kategori_rows:
            obj = models.KategoriProduk(nama_kategori=nama)
            db.add(obj)
            db.flush()
            kategori_map[nama] = obj

        toko_rows = [
            {
                "user": "penjual1",
                "nama_toko": "Toko Seragam Raimuna",
                "deskripsi": "Toko resmi perlengkapan Pramuka untuk kegiatan Raimuna Daerah.",
                "nomor_rekening": "1234-5678-9012",
                "nama_bank": "BRI",
                "pemilik": "Bambang Sutrisno",
                "wa": "0812-0005",
                "alamat": "Jl. Raya Banjar No. 8, Kabupaten Bandung",
                "status": "aktif",
            },
            {
                "user": "penjual2",
                "nama_toko": "Kerajinan Nadia",
                "deskripsi": "Kerajinan tangan khas Pramuka dan camilan UMKM lokal.",
                "nomor_rekening": "9876-5432-1098",
                "nama_bank": "BCA",
                "pemilik": "Nadia Putri",
                "wa": "0812-0004",
                "alamat": "Jl. Dago No. 12, Bandung",
                "status": "aktif",
            },
            {
                "user": "penjual3",
                "nama_toko": "Snack Kampung Rizky",
                "deskripsi": "Oleh-oleh makanan olahan khas Jawa Barat.",
                "nomor_rekening": "5555-0000-1111",
                "nama_bank": "Mandiri",
                "pemilik": "Rizky Pratama",
                "wa": "0812-0003",
                "alamat": "Jl. Raya Banjar No. 8, Kabupaten Bandung",
                "status": "pending",
            },
        ]
        toko_map = {}
        for t in toko_rows:
            toko = models.Toko(
                user_id=penjual_map[t["user"]].id,
                nama_toko=t["nama_toko"],
                deskripsi=t["deskripsi"],
                logo_url=foto_url,
                nomor_rekening=t["nomor_rekening"],
                nama_bank=t["nama_bank"],
                nama_pemilik_rekening=t["pemilik"],
                nomor_wa=t["wa"],
                alamat=t["alamat"],
                status=t["status"],
            )
            db.add(toko)
            db.flush()
            toko_map[t["nama_toko"]] = toko

        produk_rows = [
            {"toko": "Toko Seragam Raimuna", "kategori": "Seragam & Atribut", "nama": "Baju Pramuka Lengkap", "harga": 125000, "stok": 30},
            {"toko": "Toko Seragam Raimuna", "kategori": "Seragam & Atribut", "nama": "Set Kacu & Tali", "harga": 15000, "stok": 100},
            {"toko": "Toko Seragam Raimuna", "kategori": "Alat Kemah", "nama": "Tenda Dome 4 Orang", "harga": 550000, "stok": 12},
            {"toko": "Toko Seragam Raimuna", "kategori": "Alat Kemah", "nama": "Botol Minum Pramuka", "harga": 45000, "stok": 40},
            {"toko": "Kerajinan Nadia", "kategori": "Kerajinan Tangan", "nama": "Bros Tali Kur", "harga": 20000, "stok": 80},
            {"toko": "Kerajinan Nadia", "kategori": "Kerajinan Tangan", "nama": "Tas Rajut Pramuka", "harga": 120000, "stok": 25},
            {"toko": "Kerajinan Nadia", "kategori": "Makanan Olahan", "nama": "Kue Mochi Cokelat", "harga": 25000, "stok": 60},
            {"toko": "Snack Kampung Rizky", "kategori": "Makanan Olahan", "nama": "Keripik Pisang", "harga": 12000, "stok": 100},
            {"toko": "Snack Kampung Rizky", "kategori": "Makanan Olahan", "nama": "Abon Sapi Bandung", "harga": 50000, "stok": 50},
        ]
        produk_map = {}
        for p in produk_rows:
            produk = models.Produk(
                toko_id=toko_map[p["toko"]].id,
                kategori_id=kategori_map[p["kategori"]].id,
                nama_produk=p["nama"],
                harga=p["harga"],
                stok=p["stok"],
                foto_url=foto_url,
                status="aktif",
            )
            db.add(produk)
            db.flush()
            produk_map[p["nama"]] = produk

        pesanan_rows = [
            {
                "toko": "Toko Seragam Raimuna",
                "nama_pembeli": "Ibu Dewi Anggraeni",
                "kontak": "0813-0001",
                "alamat": "Jl. Asia Afrika No. 25, Bandung",
                "items": [("Baju Pramuka Lengkap", 2), ("Tenda Dome 4 Orang", 1)],
                "status": "selesai",
                "bukti": bukti_url,
                "days_ago": 6,
            },
            {
                "toko": "Toko Seragam Raimuna",
                "nama_pembeli": "Kak. Siti Nurhaliza",
                "kontak": "0812-0002",
                "alamat": "Jl. Pendidikan No. 1, Soreang",
                "items": [("Botol Minum Pramuka", 3)],
                "status": "menunggu_konfirmasi",
                "bukti": bukti_url,
                "days_ago": 2,
            },
            {
                "toko": "Kerajinan Nadia",
                "nama_pembeli": "Kak. Ahmad Fauzi",
                "kontak": "0812-0001",
                "alamat": "Jl. Merdeka No. 10, Soreang",
                "items": [("Kue Mochi Cokelat", 5)],
                "status": "menunggu_pembayaran",
                "bukti": None,
                "days_ago": 0,
            },
        ]

        for item in pesanan_rows:
            toko = toko_map[item["toko"]]
            total = 0
            detail = []
            for nama_produk, jumlah in item["items"]:
                produk = produk_map[nama_produk]
                subtotal = produk.harga * jumlah
                total += subtotal
                detail.append((produk, jumlah, subtotal))
            pesanan = models.Pesanan(
                nomor_pesanan=_buat_nomor_pesanan(db),
                pembeli_user_id=None,
                toko_id=toko.id,
                nama_pembeli=item["nama_pembeli"],
                kontak_pembeli=item["kontak"],
                alamat_pengiriman=item["alamat"],
                total_harga=total,
                status=item["status"],
                bukti_transfer_url=item["bukti"],
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
            if item["days_ago"]:
                pesanan.created_at = datetime.utcnow() - timedelta(days=item["days_ago"])

        db.commit()
        print(
            "Seeding marketplace berhasil: 3 user penjual, 3 toko (2 aktif, 1 pending), "
            "4 kategori, 9 produk, 3 pesanan contoh."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_dummy_data()
    seed_kegiatan_internal()
    seed_kontributor()
    seed_persuratan()
    seed_pelaporan()
    seed_marketplace()
