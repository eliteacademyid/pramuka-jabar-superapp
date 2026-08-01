# Requirements Document

Modul: Data Potensi Keanggotaan (Gerakan Pramuka)

## 1. Pendahuluan

Modul Data Potensi Keanggotaan adalah basis data terpusat untuk mencatat profil dan potensi anggota Gerakan Pramuka mulai dari jenjang Siaga (S), Penggalang (G), Penegak (T), Pandega (D), hingga Anggota Dewasa (Pembina/Andalan/Pelatih). Modul ini mendukung administrasi keanggotaan, pencarian data, pemetaan kompetensi (SKU/SKK/TKK dan kompetensi Pembina/Pelatih), serta rekapitulasi/laporan anggota di tingkat Gugus Depan (Gudep) hingga Kwartir.

Konteks integrasi: Modul ini merupakan satu sub-menu/modul di dalam Kwarda SuperApp (bukan aplikasi berdiri sendiri). Login, hak akses (RBAC), serta master data wilayah dan gudep dipakai bersama (shared) dengan modul-modul lain SuperApp (mis. Kegiatan, Keuangan/Iuran, Persuratan). Requirement di dokumen ini fokus pada domain Keanggotaan; kebutuhan autentikasi terpusat dan master data wilayah/gudep mengikuti standar yang sudah/akan ditetapkan oleh Core SuperApp.

### 1.1 Glosarium

Istilah Arti
Gudep Gugus Depan, satuan pendidikan pramuka berbasis pangkalan (sekolah/komunitas)
Kwarran/Kwarcab/Kwarda/Kwarnas Kwartir Ranting/Cabang/Daerah/Nasional
SKU Syarat Kecakapan Umum
SKK Syarat Kecakapan Khusus
TKK Tanda Kecakapan Khusus
Mabigus Majelis Pembimbing Gugus Depan
Andalan Pengurus Kwartir
NTA Nomor Tanda Anggota

### 1.2 Aktor Pengguna

Admin Gudep — mengelola data anggota di gudepnya.
Admin Kwartir (Ranting/Cabang/Daerah/Nasional) — melihat & merekap data lintas gudep sesuai wilayah binaannya.
Pembina/Pelatih — menginput capaian kompetensi anggota binaannya.
Anggota Dewasa — dapat melihat & melengkapi profil serta potensi/kompetensi diri sendiri.
Super Admin/Sistem — mengelola master data, hak akses, dan konfigurasi sistem.

## 2. Functional Requirements (format EARS)

### FR-1 Manajemen Profil Anggota

User Story: Sebagai Admin Gudep, saya ingin mencatat dan mengelola profil anggota di semua jenjang, agar data keanggotaan gudep saya lengkap dan akurat.

Acceptance Criteria:

- WHEN Admin Gudep menambahkan anggota baru, THE SYSTEM SHALL menyimpan data identitas (NTA, nama, tanggal lahir, jenis kelamin, alamat, kontak, foto), jenjang (Siaga/Penggalang/Penegak/Pandega/Dewasa), dan gudep asal.
- WHEN jenjang anggota dipilih, THE SYSTEM SHALL menampilkan form atribut spesifik jenjang (contoh: nama barung/regu/sangga/racana, golongan usia).
- IF anggota berusia di luar rentang jenjang yang dipilih (misal Siaga di luar 7–10 tahun), THEN THE SYSTEM SHALL menampilkan peringatan validasi namun tetap mengizinkan penyimpanan dengan catatan.
- WHEN anggota naik jenjang (misal Siaga → Penggalang), THE SYSTEM SHALL menyediakan fitur mutasi jenjang dan mencatat riwayat jenjang sebelumnya.
- WHEN data anggota diperbarui, THE SYSTEM SHALL menyimpan log riwayat perubahan (audit trail) beserta waktu dan pengubah.
- WHERE anggota adalah Anggota Dewasa, THE SYSTEM SHALL menyimpan atribut tambahan berupa peran (Pembina/Pelatih/Andalan/Mabigus) dan sertifikasi kursus (KMD/KML/KPD/KPL).

### FR-2 Pencarian & Filter Data Anggota

User Story: Sebagai pengguna sistem, saya ingin mencari dan memfilter data anggota dengan cepat, agar saya dapat menemukan anggota tertentu atau kelompok anggota sesuai kriteria.

Acceptance Criteria:

- WHEN pengguna memasukkan kata kunci pencarian, THE SYSTEM SHALL menampilkan hasil pencarian berdasarkan nama, NTA, atau nama gudep dalam waktu kurang dari 2 detik.
- THE SYSTEM SHALL menyediakan filter kombinasi berdasarkan jenjang, jenis kelamin, wilayah (Kwarcab/Kwarran), status keaktifan, dan rentang usia.
- WHEN hasil pencarian kosong, THE SYSTEM SHALL menampilkan pesan informatif dan saran memperluas kriteria.
- THE SYSTEM SHALL mendukung ekspor hasil pencarian/filter ke format Excel (.xlsx) dan PDF.
- WHERE pengguna adalah Admin Gudep, THE SYSTEM SHALL membatasi hasil pencarian hanya pada anggota di gudepnya sendiri (data scoping berbasis peran/wilayah).

### FR-3 Pemetaan Kompetensi & Potensi

User Story: Sebagai Pembina, saya ingin memetakan capaian SKU/SKK/TKK dan potensi/minat anggota, agar pembinaan dapat diarahkan sesuai bakat masing-masing anggota.

Acceptance Criteria:

- WHEN Pembina mencatat pencapaian SKU/SKK, THE SYSTEM SHALL menyimpan tanggal pencapaian, jenis kecakapan, dan tingkat (untuk SKU: Mula/Bantu/Tata, dsb sesuai jenjang).
- THE SYSTEM SHALL menyediakan daftar master SKU/SKK/TKK yang berbeda sesuai jenjang anggota (Siaga/Penggalang/Penegak/Pandega).
- WHEN seluruh SKU pada suatu tingkat telah tercapai, THE SYSTEM SHALL menandai status kenaikan tingkat secara otomatis dan memberi notifikasi kepada Pembina.
- THE SYSTEM SHALL menyediakan form pencatatan minat/bakat/potensi non-formal (misal: seni, olahraga, teknologi, kepemimpinan) yang dapat diisi bebas dan dipetakan ke kategori potensi.
- THE SYSTEM SHALL menghasilkan visualisasi (grafik/radar chart) profil kompetensi per anggota dan agregat per gudep.
- WHERE anggota adalah Anggota Dewasa, THE SYSTEM SHALL memetakan kompetensi berbasis sertifikasi kursus dan bidang keahlian pembinaan.

### FR-4 Rekapitulasi & Pelaporan

User Story: Sebagai Admin Kwartir, saya ingin melihat rekapitulasi jumlah dan potensi anggota lintas gudep, agar saya dapat menyusun program pembinaan dan laporan organisasi.

Acceptance Criteria:

- THE SYSTEM SHALL menampilkan dashboard rekapitulasi jumlah anggota per jenjang, jenis kelamin, dan wilayah.
- THE SYSTEM SHALL menghasilkan laporan periodik (bulanan/tahunan) jumlah anggota aktif, anggota baru, dan anggota naik jenjang.
- WHEN Admin Kwartir memilih rentang wilayah (Kwarran/Kwarcab/Kwarda), THE SYSTEM SHALL mengagregasi data hanya dari gudep dalam wilayah tersebut.
- THE SYSTEM SHALL menyediakan unduhan laporan dalam format PDF dan Excel yang siap cetak.
- THE SYSTEM SHALL menampilkan tren perkembangan jumlah anggota dalam bentuk grafik garis per periode waktu.

### FR-5 Administrasi & Manajemen Akses

User Story: Sebagai Super Admin, saya ingin mengatur hak akses dan master data spesifik modul Keanggotaan, agar sistem digunakan sesuai peran dan data tetap konsisten, tanpa menduplikasi apa yang sudah dikelola Core SuperApp.

Acceptance Criteria:

- THE SYSTEM SHALL menggunakan sesi/token autentikasi yang diterbitkan oleh Core Auth Service SuperApp (single sign-on); modul ini tidak menyediakan form login terpisah.
- THE SYSTEM SHALL menerapkan kontrol akses berbasis peran (RBAC) dengan membaca klaim peran dari token Core: Super Admin, Admin Kwartir (per level), Admin Gudep, Pembina, Anggota.
- WHEN pengguna mencoba mengakses data di luar cakupan wilayah/perannya, THE SYSTEM SHALL menolak akses dan mencatat percobaan pada log keamanan.
- THE SYSTEM SHALL mengonsumsi master data wilayah dan gudep dari Core SuperApp (bukan mengelola sendiri), dan hanya menyediakan pengelolaan master data yang spesifik pada domainnya sendiri: daftar SKU/SKK/TKK dan kategori potensi.
- THE SYSTEM SHALL menyediakan fitur impor data massal (bulk import) anggota melalui template Excel dengan validasi otomatis.
- IF berkas impor mengandung data tidak valid, THEN THE SYSTEM SHALL menampilkan daftar baris bermasalah tanpa menggagalkan keseluruhan proses impor data valid lainnya.
- THE SYSTEM SHALL mengirim event/log audit penting (create/update/delete data anggota) ke layanan log audit terpusat SuperApp, jika layanan tersebut tersedia.

### FR-6 Navigasi & Integrasi Menu dalam SuperApp

User Story: Sebagai pengguna SuperApp, saya ingin fitur Keanggotaan tampil sebagai satu grup menu yang menyatu dengan modul-modul lain, agar saya tidak perlu berpindah aplikasi untuk mengakses fitur-fitur Kwarda.

Acceptance Criteria:

- THE SYSTEM SHALL menyediakan menu modul ini sebagai satu grup submenu ("Keanggotaan") yang terpasang (mounted) di dalam shell navigasi utama Kwarda SuperApp, berisi: Dashboard Keanggotaan, Data Anggota (per jenjang), Pemetaan Kompetensi, Rekapitulasi & Laporan, dan Administrasi Keanggotaan.
- WHEN pengguna login ke SuperApp, THE SYSTEM SHALL menampilkan grup menu "Keanggotaan" hanya jika peran pengguna memiliki hak akses terhadap modul ini (menu dinamis lintas modul, dikendalikan oleh Core).
- THE SYSTEM SHALL menyediakan breadcrumb navigasi yang mencerminkan hierarki penuh SuperApp (mis. SuperApp / Keanggotaan / Data Anggota / Penggalang).
- THE SYSTEM SHALL bersifat responsif dan dapat diakses melalui tampilan desktop maupun mobile mengikuti shell/layout SuperApp yang berlaku.
- THE SYSTEM SHALL menyediakan API internal agar modul lain di SuperApp (mis. modul Keuangan/Iuran) dapat mengambil data dasar anggota (nama, NTA, jenjang, gudep) tanpa perlu mengakses database modul ini secara langsung.

## 3. Non-Functional Requirements

- Keamanan: Data pribadi anggota (khususnya anak di bawah umur) WAJIB dienkripsi saat disimpan (at rest) dan saat transmisi (in transit, HTTPS/TLS).
- Kepatuhan: Sistem SHALL mematuhi prinsip perlindungan data pribadi (mis. UU PDP) khususnya untuk data anggota di bawah 18 tahun (Siaga, Penggalang, Penegak, sebagian Pandega).
- Performa: Sistem SHALL mampu menangani hingga 100.000 data anggota dengan waktu respons pencarian < 3 detik.
- Ketersediaan: Sistem SHALL memiliki uptime minimal 99% di luar jadwal pemeliharaan terjadwal.
- Skalabilitas: Arsitektur SHALL mendukung penambahan wilayah/kwartir baru tanpa perubahan struktur data mayor.
- Auditabilitas: Seluruh perubahan data penting SHALL tercatat dalam log audit yang dapat ditelusuri.
- Usabilitas: Antarmuka SHALL mengikuti prinsip aksesibilitas dasar (kontras warna, ukuran font terbaca, navigasi keyboard).

## 4. Batasan (Out of Scope)

- Dokumen ini tidak mendefinisikan ulang fitur Core SuperApp yang sudah/akan ada: autentikasi SSO, manajemen pengguna lintas modul, dan master data wilayah/gudep — modul ini hanya mengonsumsinya.
- Modul ini tidak mencakup sistem keuangan/iuran anggota (modul terpisah dalam SuperApp; berintegrasi via API data dasar anggota).
- Modul ini tidak mencakup sistem presensi kegiatan harian secara real-time (modul terpisah dalam SuperApp).
- Integrasi dengan sistem SIPP Pramuka Nasional (jika ada) bersifat opsional dan didefinisikan di fase lanjutan.
- Desain shell/layout global SuperApp (header, sidebar utama, tema) mengikuti standar SuperApp yang sudah ada; dokumen ini hanya mendefinisikan submenu di dalamnya.
