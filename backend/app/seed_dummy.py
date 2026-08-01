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


if __name__ == "__main__":
    seed_dummy_data()
