# Software Design Document (SDD)
## Modul: e-Pelatihan dan Sertifikasi Digital

### 1. Pendahuluan
#### 1.1 Tujuan
Dokumen Spesifikasi Desain Perangkat Lunak (SDD) ini bertujuan untuk memberikan gambaran arsitektur, desain, dan spesifikasi detail dari modul **e-Pelatihan dan Sertifikasi Digital**. Dokumen ini ditujukan bagi pengembang, desainer, QA, dan pemangku kepentingan (stakeholder) sebagai acuan utama dalam proses pengembangan modul.

#### 1.2 Ruang Lingkup
Modul **e-Pelatihan dan Sertifikasi Digital** adalah sebuah *Learning Management System* (LMS) mini yang diintegrasikan ke dalam sistem utama. Ruang lingkup modul ini meliputi:
- Penyediaan daftar pelatihan yang tersedia.
- Penyampaian materi belajar (modul bacaan, video, dsb).
- Pencatatan dan pemantauan progres belajar peserta.
- Penyelenggaraan kuis online sebagai alat evaluasi.
- Sistem penilaian otomatis berbasis kriteria yang telah ditentukan.
- Penerbitan sertifikat digital secara otomatis bagi peserta yang memenuhi syarat kelulusan.

#### 1.3 Definisi dan Akronim
- **LMS (Learning Management System):** Sistem perangkat lunak untuk administrasi, dokumentasi, pelacakan, pelaporan, dan penyampaian program pendidikan/pelatihan.
- **Admin/Instruktur:** Pengguna yang memiliki hak akses untuk membuat, mengelola, dan mengawasi jalannya pelatihan, materi, serta kuis.
- **Peserta:** Pengguna (anggota Pramuka/umum) yang mendaftar dan mengikuti pelatihan.
- **Sertifikat Digital:** Dokumen bukti kelulusan berformat digital (PDF/Image) yang diterbitkan secara otomatis oleh sistem.

---

### 2. Deskripsi Keseluruhan
#### 2.1 Perspektif Produk
Modul ini merupakan bagian (sub-sistem) dari aplikasi super-app / portal informasi utama. Modul ini berinteraksi erat dengan modul Autentikasi/Manajemen Pengguna untuk memverifikasi data profil peserta yang akan dicantumkan pada sertifikat.

#### 2.2 Fungsi Utama
1. **Katalog Pelatihan:** Menampilkan daftar pelatihan yang aktif, akan datang, dan selesai.
2. **Manajemen Materi:** Fasilitas bagi instruktur untuk mengunggah materi belajar berurut.
3. **Tracking Progres:** Menampilkan persentase atau checklist penyelesaian materi oleh peserta.
4. **Sistem Evaluasi (Kuis):** Fitur untuk mengerjakan kuis dengan waktu terbatas atau tidak terbatas.
5. **Auto-Grading:** Penilaian instan setelah peserta menyelesaikan kuis.
6. **E-Certificate Generator:** Membuat dan mengirim/menyediakan tautan unduh sertifikat ber-QR code bagi peserta yang lulus.

#### 2.3 Karakteristik Pengguna
- **Peserta (End-User):** Membutuhkan antarmuka yang intuitif (mobile-friendly), interaktif, dan mudah dinavigasi.
- **Instruktur/Admin:** Membutuhkan *dashboard* untuk mengelola konten pembelajaran (CRUD materi, soal kuis) dan melihat analitik peserta.

---

### 3. Spesifikasi Kebutuhan Fungsional (Functional Requirements)

| ID | Fitur | Deskripsi | Aktor |
|---|---|---|---|
| FR-01 | Daftar Pelatihan | Sistem dapat menampilkan daftar pelatihan beserta deksripsi, jadwal, dan kuota. | Peserta, Admin |
| FR-02 | Pendaftaran Pelatihan | Sistem memungkinkan pengguna mendaftar ke pelatihan tertentu. | Peserta |
| FR-03 | Manajemen Modul Belajar | Sistem memungkinkan penambahan, pengubahan, penghapusan topik/modul belajar dalam suatu pelatihan. | Admin |
| FR-04 | Akses Materi | Sistem dapat menampilkan materi berupa teks, dokumen (PDF), atau embedded video. | Peserta |
| FR-05 | Pencatatan Progres | Sistem dapat menandai otomatis (atau manual) materi yang telah diselesaikan dan menampilkan persentase progres (0-100%). | Peserta |
| FR-06 | Manajemen Kuis | Sistem memfasilitasi pembuatan soal (pilihan ganda, dsb), pengaturan bobot nilai, dan batas waktu kuis. | Admin |
| FR-07 | Pelaksanaan Kuis | Sistem menampilkan soal kuis dan menerima jawaban dari peserta, mengunci soal setelah disubmit atau waktu habis. | Peserta |
| FR-08 | Penilaian Otomatis | Sistem langsung menghitung skor kuis berdasarkan kunci jawaban yang ada. | Sistem |
| FR-09 | Penerbitan Sertifikat | Sistem men-generate e-Sertifikat (PDF) dengan nama peserta jika skor akhir mencapai *passing grade*. | Sistem |
| FR-10 | Validasi Sertifikat | Sistem menyediakan QR code pada e-Sertifikat untuk verifikasi keaslian via link URL. | Publik, Sistem |

---

### 4. Desain Basis Data (Database Architecture)

Berikut adalah rancangan entitas utama yang dibutuhkan (struktur ERD):

#### 4.1 Tabel `trainings` (Pelatihan)
Menyimpan data master pelatihan.
- `id` (PK)
- `title` (String)
- `description` (Text)
- `start_date` (DateTime)
- `end_date` (DateTime)
- `passing_grade` (Integer)
- `status` (Enum: Draft, Published, Closed)

#### 4.2 Tabel `training_materials` (Materi Belajar)
Menyimpan daftar materi/modul di tiap pelatihan.
- `id` (PK)
- `training_id` (FK -> trainings.id)
- `title` (String)
- `content` (Text/HTML)
- `media_url` (String - opsional untuk link video/PDF)
- `order` (Integer - urutan materi)

#### 4.3 Tabel `quizzes` (Kuis)
Menyimpan data kuis yang terkait dengan pelatihan.
- `id` (PK)
- `training_id` (FK -> trainings.id)
- `title` (String)
- `time_limit_minutes` (Integer)

#### 4.4 Tabel `quiz_questions` (Soal Kuis)
Menyimpan butir soal untuk kuis tertentu.
- `id` (PK)
- `quiz_id` (FK -> quizzes.id)
- `question_text` (Text)
- `options` (JSON - menyimpan array pilihan ganda)
- `correct_answer` (String)
- `score_weight` (Integer)

#### 4.5 Tabel `enrollments` (Partisipasi Peserta)
Menyimpan data peserta yang mendaftar pelatihan.
- `id` (PK)
- `user_id` (FK -> users.id)
- `training_id` (FK -> trainings.id)
- `progress_percentage` (Decimal)
- `status` (Enum: Enrolled, Completed, Dropped)
- `enrolled_at` (Timestamp)

#### 4.6 Tabel `quiz_attempts` (Hasil Kuis Peserta)
Menyimpan data hasil pengerjaan kuis.
- `id` (PK)
- `enrollment_id` (FK -> enrollments.id)
- `quiz_id` (FK -> quizzes.id)
- `score` (Decimal)
- `passed` (Boolean)
- `attempted_at` (Timestamp)

#### 4.7 Tabel `certificates` (Sertifikat Digital)
Menyimpan data sertifikat yang diterbitkan.
- `id` (PK, UUID) - Sebagai nomor identifikasi unik sertifikat
- `enrollment_id` (FK -> enrollments.id)
- `certificate_url` (String)
- `issued_at` (Timestamp)

---

### 5. Arsitektur dan Alur Sistem (System Flow)

#### 5.1 Alur Pengguna (User Flow) Mengikuti Pelatihan
1. **Registrasi:** Peserta melihat daftar pelatihan dan klik "Daftar".
2. **Belajar:** Peserta masuk ke dashboard pelatihan, melihat daftar materi.
3. **Progres:** Setiap kali peserta menekan "Selesai Baca" / menonton materi hingga habis, progres di-update di sistem.
4. **Evaluasi:** Setelah progres 100% (atau mencapai syarat tertentu), menu kuis terbuka.
5. **Kuis:** Peserta mengerjakan kuis. Setelah selesai disubmit.
6. **Penilaian:** Sistem memeriksa skor. Jika memenuhi *passing grade*, status pelatihan menjadi *Completed*.
7. **Sertifikat:** Sistem memanggil *service generator PDF* untuk membuat sertifikat. Tautan sertifikat muncul di halaman profil peserta.

---

### 6. Desain API (API Endpoints)
Draft REST API yang akan digunakan antara Frontend dan Backend:

**Peserta (End-User):**
- `GET /api/trainings` - Mendapatkan daftar pelatihan.
- `POST /api/trainings/{id}/enroll` - Mendaftar pelatihan.
- `GET /api/trainings/{id}/materials` - Mengambil daftar materi pelatihan.
- `POST /api/trainings/materials/{materi_id}/complete` - Menandai materi selesai.
- `GET /api/quizzes/{id}` - Memulai/Mengambil soal kuis.
- `POST /api/quizzes/{id}/submit` - Mensubmit jawaban kuis (mereturn kalkulasi *score*).
- `GET /api/certificates/{id}/download` - Mengunduh e-Sertifikat.

**Admin/Instruktur:**
- `POST /api/admin/trainings` - Membuat pelatihan baru.
- `POST /api/admin/trainings/{id}/materials` - Menambah materi baru.
- `POST /api/admin/quizzes` - Mengatur kuis dan butir soal kuis.
- `GET /api/admin/trainings/{id}/reports` - Melihat laporan kelulusan peserta.

---

### 7. Kebutuhan Non-Fungsional (Non-Functional Requirements)
1. **Keamanan:**
   - Validasi sesi pengerjaan kuis untuk menghindari kecurangan (manipulasi waktu).
   - Akses materi pelatihan tidak bisa bypass tanpa pendaftaran (*enrollment*).
   - QR Code sertifikat harus mengarah ke tautan validasi resmi yang *read-only*.
2. **Kinerja (Performance):**
   - Sertifikat digital harus di-generate via *asynchronous background job* (misal: Redis / RabbitMQ queue + worker) agar pengguna tidak menunggu *loading* lama saat Submit Kuis.
3. **Penyimpanan:**
   - Dokumen sertifikat sebaiknya disimpan di cloud storage (misal: AWS S3 atau Google Cloud Storage) untuk kemudahan akses dan mengurangi beban *local storage* server.
