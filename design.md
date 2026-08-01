# User Interface & Experience Design (UI/UX)
## Modul: e-Pelatihan dan Sertifikasi Digital

Dokumen ini menjelaskan rancangan tata letak (*layout*), pengalaman pengguna (*user experience*), dan struktur halaman (*sitemap*) untuk modul **e-Pelatihan dan Sertifikasi Digital**.

---

### 1. Struktur Halaman (Sitemap)

#### Bagian Pengguna (Peserta)
- **Beranda Pelatihan (`/trainings`)**
  - Menampilkan daftar semua pelatihan yang tersedia, sedang berjalan, atau sudah selesai.
- **Detail Pelatihan (`/trainings/{id}`)**
  - Menampilkan deskripsi lengkap pelatihan, jadwal, instruktur, prasyarat, dan tombol "Daftar".
- **Ruang Belajar / *Learning Room* (`/trainings/{id}/learn`)**
  - Halaman utama saat peserta mengikuti pelatihan. Menampilkan daftar materi di panel samping (sidebar) dan konten materi di panel utama.
- **Halaman Kuis (`/trainings/{id}/quiz`)**
  - Halaman khusus untuk mengerjakan soal kuis.
- **Halaman Hasil & Sertifikat (`/trainings/{id}/certificate`)**
  - Halaman untuk melihat skor kuis, status kelulusan, dan tombol unduh sertifikat (PDF).

#### Bagian Admin / Instruktur
- **Dashboard Admin Pelatihan (`/admin/trainings`)**
  - Tabel daftar pelatihan yang ada.
- **Form Kelola Pelatihan (`/admin/trainings/edit`)**
  - CRUD informasi umum pelatihan.
- **Manajemen Materi & Kuis (`/admin/trainings/{id}/builder`)**
  - Antarmuka drag-and-drop atau form terstruktur untuk menambah modul materi dan soal kuis.
- **Laporan Peserta (`/admin/trainings/{id}/participants`)**
  - Tabel progres peserta, nilai kuis, dan status kelulusan.

---

### 2. Deskripsi Wireframe / Tata Letak

#### 2.1 Beranda Pelatihan (Daftar Pelatihan)
- **Header:** Judul "Katalog e-Pelatihan" dengan kotak pencarian dan filter (Kategori, Status).
- **Body:** Menggunakan *Grid Layout* berisi *Card* Pelatihan.
- **Isi Card Pelatihan:** 
  - Gambar/Thumbnail pelatihan.
  - Judul Pelatihan.
  - Badge Status (Pendaftaran Buka/Tutup).
  - Deskripsi singkat (max 2 baris).
  - Tombol "Lihat Detail".

#### 2.2 Detail Pelatihan
- **Hero Section:** Banner besar dengan judul, tanggal pelaksanaan, dan kuota.
- **Main Content:**
  - **Kiri (2/3 lebar):** Deskripsi detail, tujuan pembelajaran, dan silabus (daftar materi yang akan dipelajari).
  - **Kanan (1/3 lebar):** Kotak info (Progress bar jika sudah mendaftar, tombol "Daftar Sekarang" jika belum).

#### 2.3 Ruang Belajar (Learning Room)
- **Layout Split-Screen:**
  - **Sidebar Kiri (25% lebar):** Daftar isi/modul. Memiliki ikon *checklist* (✅) di sebelah materi yang sudah selesai dibaca. Terdapat progress bar (contoh: "60% Selesai").
  - **Main Area Kanan (75% lebar):** Area untuk menampilkan teks panjang (Markdown/HTML), PDF *viewer*, atau pemutar video (YouTube/Local).
  - **Footer Main Area:** Tombol "Tandai Selesai & Lanjut" (Tombol ini mendisable jika materi berupa video yang belum selesai ditonton, *opsional*).

#### 2.4 Halaman Kuis
- **Header:** Judul Kuis, dan *Timer* mundur (Countdown) di pojok kanan atas yang menempel (sticky).
- **Body:** 
  - Pertanyaan tampil satu per satu atau semua dalam satu halaman (tergantung preferensi, disarankan 1 halaman dengan urutan vertikal).
  - Opsi jawaban menggunakan *Radio Button* berukuran besar yang mudah di-tap di perangkat mobile.
- **Footer:** Tombol "Kumpulkan Jawaban".

#### 2.5 Halaman Hasil & Sertifikat
- **State LULUS:**
  - Ikon Checklist/Piala besar warna hijau.
  - Teks: "Selamat! Anda lulus dengan skor 85."
  - Tombol utama: "Unduh e-Sertifikat" (Warna primer).
- **State GAGAL:**
  - Ikon Silang/Peringatan warna merah.
  - Teks: "Maaf, skor Anda (50) belum memenuhi batas kelulusan (75)."
  - Tombol utama: "Ulangi Kuis" (jika diperbolehkan).

---

### 3. Komponen UI (UI Components)

- **Progress Bar:** Indikator visual horizontal berwarna hijau (saat selesai) atau biru (saat berjalan) untuk menandakan sejauh mana peserta menyelesaikan materi.
- **Status Badge:** Label kecil (Pill) untuk status pelatihan (Misal: Hijau="Aktif", Abu-abu="Selesai", Kuning="Draft").
- **PDF Certificate Template:** Desain latar belakang sertifikat kosong yang nantinya akan dioverlay dengan teks (Nama Peserta, Nama Pelatihan, Tanggal, dan QR Code) menggunakan *backend generator*.

---

### 4. Alur Interaksi (User Experience Flow)

1. **Onboarding:** Saat pertama kali masuk Ruang Belajar, sistem memberikan *tooltip* singkat (Contoh: "Klik tombol Selesai untuk merekam progres Anda").
2. **Kunci Akses (Gating):** Menu kuis akan terkunci (*disabled*) dan berwarna abu-abu di sidebar sampai progres materi mencapai 100%.
3. **Mencegah Hilang Data:** Jika peserta sedang mengerjakan kuis dan mencoba menutup tab/kembali, muncul *browser alert*: "Anda sedang mengerjakan kuis. Jawaban Anda mungkin tidak tersimpan."
4. **Validasi Instan:** Setelah kuis dikumpulkan, *loading screen* muncul maksimal 2 detik, lalu langsung beralih ke halaman hasil (karena *auto-grading* berjalan cepat di backend).

---

### 5. Panduan Visual (Responsiveness)
- Semua halaman wajib **Mobile-First**. Tabel pada Dashboard Admin harus bisa digeser (*horizontal scroll*) di perangkat kecil atau diubah menjadi tampilan daftar (List).
- Tombol navigasi (seperti "Selanjutnya") dibuat cukup besar (minimal 44x44 pixel) untuk mempermudah akses di layar sentuh.
