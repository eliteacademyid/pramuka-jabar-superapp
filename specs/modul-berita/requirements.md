# Spec: Modul Berita — Super Apps Pramuka Jawa Barat

> Metode: Spec-Driven Development (Specs) — Requirements-First
> Status: **Menunggu Approval Gate 1**

## Problem Statement

Super Apps Pramuka Jawa Barat (v1.0) saat ini hanya memiliki landing page statis,
login, dashboard, dan manajemen user. Kwartir Daerah Jawa Barat membutuhkan kanal
informasi publik berupa **berita** agar organisasi dapat menyampaikan kegiatan,
pengumuman, dan prestasi kepada masyarakat. Modul ini menjadi fondasi untuk
modul-modul konten lain (kegiatan, galeri, dokumen) di iterasi berikutnya.

Modul Berita harus menyediakan:

1. Pengelolaan berita oleh admin (CRUD lengkap, termasuk unggah gambar sampul).
2. Publikasi berita dengan alur **draft → published**, hanya berita *published*
   yang tampil di halaman publik.
3. Halaman publik berita (daftar + detail) tanpa autentikasi.
4. Halaman admin berita dengan **pagination, pencarian, dan filter**.
5. Kategori berita berupa **list tetap** (master data kategori di P1).

## Scope

### P0 — Dalam Scope (iterasi ini)

| Area | Cakupan |
|---|---|
| Backend | CRUD berita, upload gambar, publikasi draft/published, list publik, detail publik, pagination, pencarian, filter status/kategori, seed data sintetis |
| Frontend | Halaman publik berita (list + detail), halaman admin manajemen berita (tabel, pagination, pencarian, filter), form tambah/edit dengan upload gambar, hapus dengan konfirmasi |
| Infrastruktur | Volume penyimpanan gambar pada deployment kontainer (docker-compose) |

### P1 — Di luar Scope (iterasi berikutnya, ditandai `[P1]`)

- Master data kategori (CRUD) — P0 memakai list tetap
- Soft delete & restore berita — P0 memakai hard delete
- Workflow approval "staff menulis, admin publish" — P0: admin saja
- Editor rich text — P0: konten berupa teks biasa (textarea)
- Slug untuk URL ramah-SEO
- Statistik tampilan berita
- Jadwal publish (scheduled publish)

## Definisi

| Istilah | Definisi |
|---|---|
| Berita | Artikel konten dengan judul, konten, kategori, gambar sampul, status, dan penulis |
| Kategori | Pengelompokan berita dari list tetap: `kegiatan`, `informasi`, `prestasi`, `lainnya` |
| Status | `draft` (belum tampil publik) atau `published` (tampil di halaman publik) |
| Gambar sampul | File gambar tunggal yang diunggah saat membuat/mengubah berita |
| Data sintetis | Data contoh yang tidak mengandung informasi pribadi orang sungguhan |

---

## 1. User Stories & Functional Requirements (EARS)

### US-01 — Admin membuat berita

**Sebagai** admin, **saya ingin** membuat berita baru dengan judul, konten, kategori,
dan gambar sampul, **agar** informasi dapat dipublikasikan ke publik.

| ID | Requirement (EARS) |
|---|---|
| REQ-B01 | WHEN admin mengirim permintaan pembuatan berita dengan data valid (judul, konten, kategori, status) THE SYSTEM SHALL membuat berita baru dengan penulis = admin yang sedang login dan `created_at`/`updated_at` saat itu |
| REQ-B02 | WHEN admin mengirim pembuatan berita tanpa gambar sampul THE SYSTEM SHALL tetap membuat berita dengan gambar sampul kosong |
| REQ-B03 | WHEN admin mengirim pembuatan berita dengan status `published` THE SYSTEM SHALL menetapkan `published_at` saat itu |
| REQ-B04 | WHEN admin mengirim pembuatan berita dengan data tidak valid THE SYSTEM SHALL menolak dengan pesan error yang spesifik dan kode status 400/422 |

**Acceptance Criteria US-01:**

- AC-B01: POST `/api/news` dengan token admin dan body `{judul, konten, kategori, status}` valid → 201, berita tersimpan, `penulis_id` = id admin, `gambar` kosong.
- AC-B02: POST `/api/news` dengan file gambar jpeg/png/webp ≤ 2 MB → 201, file tersimpan, kolom `gambar` berisi path/URL yang dapat diakses.
- AC-B03: POST `/api/news` dengan status `published` → `published_at` terisi; dengan status `draft` → `published_at` null.
- AC-B04: POST `/api/news` tanpa token / token non-admin → 401/403, tidak ada data tersimpan.
- AC-B05: POST `/api/news` dengan judul kosong, konten kosong, atau kategori di luar list tetap → 400 dengan `detail` menjelaskan field yang gagal.
- AC-B06: POST `/api/news` dengan file selain jpeg/png/webp atau > 2 MB → 400, file tidak tersimpan.

---

### US-02 — Admin melihat daftar berita

**Sebagai** admin, **saya ingin** melihat daftar seluruh berita (termasuk draft) dengan
pagination, pencarian, dan filter, **agar** mudah menemukan dan mengelola konten.

| ID | Requirement (EARS) |
|---|---|
| REQ-B05 | WHEN admin mengirim permintaan daftar berita dengan parameter `page` dan `page_size` THE SYSTEM SHALL mengembalikan halaman berita yang sesuai beserta metadata total & total halaman |
| REQ-B06 | WHEN admin mengirim permintaan daftar berita dengan parameter `search` THE SYSTEM SHALL mengembalikan berita yang judul atau kontennya mengandung kata kunci (case-insensitive) |
| REQ-B07 | WHEN admin mengirim permintaan daftar berita dengan parameter `status` THE SYSTEM SHALL mengembalikan hanya berita dengan status tersebut |
| REQ-B08 | WHEN admin mengirim permintaan daftar berita dengan parameter `kategori` THE SYSTEM SHALL mengembalikan hanya berita dengan kategori tersebut |

**Acceptance Criteria US-02:**

- AC-B07: GET `/api/admin/news?page=1&page_size=10` → 200 dengan `{items, total, page, page_size, total_pages}`; `total_pages` = ceil(total/page_size).
- AC-B08: GET `/api/admin/news?search=prestasi` → hanya berita yang judul/konten mengandung "prestasi" (huruf besar/kecil tidak dibedakan).
- AC-B09: GET `/api/admin/news?status=draft` → hanya berita draft; kombinasi `status=published&kategori=kegiatan` berlaku AND.
- AC-B10: Response daftar tidak menyertakan kolom internal seperti `hashed_password` (tidak ada data pengguna bocor; penulis dikembalikan sebagai objek `{id, username, nama_lengkap}`).
- AC-B11: Akses tanpa token admin → 401/403.

---

### US-03 — Admin mengubah & menghapus berita

**Sebagai** admin, **saya ingin** mengubah isi/status/gambar berita dan menghapus berita,
**agar** konten tetap akurat dan relevan.

| ID | Requirement (EARS) |
|---|---|
| REQ-B09 | WHEN admin mengirim pembaruan berita dengan field valid THE SYSTEM SHALL memperbarui field tersebut dan menetapkan `updated_at` saat itu |
| REQ-B10 | WHEN admin mengubah status menjadi `published` dari `draft` THE SYSTEM SHALL menetapkan `published_at` saat itu (tidak mengubah `published_at` jika sudah pernah published) |
| REQ-B11 | WHEN admin mengirim penggantian gambar sampul THE SYSTEM SHALL menyimpan gambar baru dan menghapus file gambar lama dari penyimpanan |
| REQ-B12 | WHEN admin mengirim penghapusan berita THE SYSTEM SHALL menghapus data berita beserta file gambar sampulnya (hard delete) |
| REQ-B13 | WHEN admin mengirim pembaruan/penghapusan berita dengan id yang tidak ada THE SYSTEM SHALL mengembalikan 404 |

**Acceptance Criteria US-03:**

- AC-B12: PUT `/api/news/{id}` dengan perubahan judul → 200, `judul` berubah, `updated_at` bertambah.
- AC-B13: PUT berita draft → status `published` → `published_at` terisi; PUT berita published (ubah konten) → `published_at` tetap tidak berubah.
- AC-B14: PUT dengan gambar baru → gambar lama terhapus dari penyimpanan (verifikasi via volume/disk).
- AC-B15: DELETE `/api/news/{id}` → 204, berita tidak muncul di daftar & detail, file gambar terhapus.
- AC-B16: PUT/DELETE id tidak ada → 404.
- AC-B17: PUT/DELETE tanpa token atau non-admin → 401/403.

---

### US-04 — Publik melihat daftar & detail berita

**Sebagai** pengunjung (publik, tanpa login), **saya ingin** melihat daftar berita
*published* dan detailnya, **agar** dapat membaca informasi organisasi.

| ID | Requirement (EARS) |
|---|---|
| REQ-B14 | WHEN pengunjung mengirim permintaan daftar berita publik THE SYSTEM SHALL mengembalikan hanya berita berstatus `published`, diurutkan `published_at` terbaru, dengan pagination |
| REQ-B15 | WHEN pengunjung mengirim permintaan detail berita `published` THE SYSTEM SHALL mengembalikan detail berita (judul, konten, kategori, gambar, penulis, tanggal publish) |
| REQ-B16 | WHEN pengunjung mengirim permintaan detail berita berstatus `draft` atau id tidak ada THE SYSTEM SHALL mengembalikan 404 |

**Acceptance Criteria US-04:**

- AC-B18: GET `/api/news` (tanpa token) → hanya berita `published`, urutan `published_at` descending, pagination berlaku.
- AC-B19: GET `/api/news/{id}` untuk berita `published` → 200 berisi judul, konten, kategori, gambar, `penulis`, `published_at`.
- AC-B20: GET `/api/news/{id}` untuk berita `draft` atau id tidak ada → 404.
- AC-B21: Parameter `search` & `kategori` berlaku juga pada list publik; parameter `status` diabaikan/dilarang pada endpoint publik (selalu `published`).

---

### US-05 — Halaman publik berita (frontend)

**Sebagai** pengunjung, **saya ingin** menjelajahi berita melalui halaman publik,
**agar** dapat membaca informasi tanpa harus login.

| ID | Requirement (EARS) |
|---|---|
| REQ-B17 | WHEN pengunjung membuka `/berita` THE SYSTEM SHALL menampilkan daftar kartu berita published (gambar, judul, kategori, tanggal) dengan pagination & pencarian |
| REQ-B18 | WHEN pengunjung mengklik salah satu berita THE SYSTEM SHALL menampilkan halaman detail berita (`/berita/{id}`) berisi konten lengkap |

**Acceptance Criteria US-05:**

- AC-B22: Halaman `/berita` menampilkan berita published; berita draft tidak muncul.
- AC-B23: Search box di halaman `/berita` memfilter daftar via parameter `search`.
- AC-B24: Halaman `/berita/{id}` menampilkan judul, kategori, tanggal publish, penulis, gambar, dan konten.
- AC-B25: URL `/berita/{id}` untuk berita draft/tidak ada menampilkan halaman "Berita tidak ditemukan" (404 diarahkan ke UI ramah).

---

### US-06 — Halaman admin manajemen berita (frontend)

**Sebagai** admin, **saya ingin** mengelola berita melalui antarmuka admin,
**agar** tidak perlu memakai API secara manual.

| ID | Requirement (EARS) |
|---|---|
| REQ-B19 | WHEN admin membuka `/admin/berita` THE SYSTEM SHALL menampilkan tabel berita (judul, kategori, status, tanggal, penulis) dengan pagination, pencarian, dan filter status/kategori |
| REQ-B20 | WHEN admin mengklik "Tambah Berita" THE SYSTEM SHALL menampilkan form (judul, konten, kategori, status, gambar sampul) dan menyimpannya melalui API |
| REQ-B21 | WHEN admin mengklik "Edit" pada sebuah berita THE SYSTEM SHALL menampilkan form terisi dan menyimpan perubahan melalui API |
| REQ-B22 | WHEN admin mengklik "Hapus" THE SYSTEM SHALL meminta konfirmasi sebelum menghapus melalui API |

**Acceptance Criteria US-06:**

- AC-B26: Menu "Manajemen Berita" muncul di sidebar admin (di bawah Manajemen User).
- AC-B27: Tabel menampilkan badge status (`Draft`/`Published`) dan filter status/kategori berfungsi.
- AC-B28: Form tambah/edit memvalidasi: judul & konten wajib, kategori wajib, ukuran gambar ≤ 2 MB.
- AC-B29: Setelah simpan/hapus, tabel dimuat ulang dan data terbaru tampil.
- AC-B30: Halaman admin dilindungi guard: tanpa token → redirect `/login`.

---

## 2. Non-Functional Requirements

| ID | Requirement (EARS) |
|---|---|
| NFR-B01 | WHEN permintaan ke endpoint berita diproses THE SYSTEM SHALL mengembalikan respons dalam ≤ 500 ms pada data sintetis ≤ 100 berita (dev environment) |
| NFR-B02 | WHEN gambar sampul disimpan THE SYSTEM SHALL membatasi ukuran maksimal 2 MB dan tipe `image/jpeg`, `image/png`, `image/webp` |
| NFR-B03 | WHEN aplikasi dijalankan ulang THE SYSTEM SHALL tetap mempertahankan data berita dan file gambar (persistence via PostgreSQL + volume) |
| NFR-B04 | WHEN data contoh di-seed THE SYSTEM SHALL menggunakan data sintetis (nama, lokasi, isi berita fiktif) tanpa data pribadi nyata |
| NFR-B05 | WHEN kode berita diimplementasikan THE SYSTEM SHALL mengikuti struktur existing (FastAPI router + SQLAlchemy + Vue 3 Composition API) agar konsisten dengan modul user |

---

## 3. Data & Privasi

- Semua data contoh (seed) adalah **data sintetis**: nama tokoh fiktif, nama gugus depan fiktif, isi berita fiktif. Tidak ada data pribadi nyata.
- Endpoint publik hanya mengembalikan data berita; tidak pernah mengembalikan data sensitif pengguna (`hashed_password`).
- File gambar diberi nama unik (UUID) agar tidak terjadi tabrakan nama.

## 4. Out of Scope (P1 — iterasi berikutnya)

| ID | Item |
|---|---|
| [P1] | Master data kategori (CRUD) |
| [P1] | Soft delete & restore |
| [P1] | Workflow staff menulis → admin publish |
| [P1] | Rich text editor |
| [P1] | Slug URL & jadwal publish |
| [P1] | Statistik tampilan berita |

---

## Traceability Matrix (awal)

| Requirement | Artefak |
|---|---|
| REQ-B01..B04 (US-01) | → design: News model, POST /api/news, upload handler → tasks → code → test |
| REQ-B05..B08 (US-02) | → design: list query pagination/search/filter |
| REQ-B09..B13 (US-03) | → design: PUT/DELETE /api/news |
| REQ-B14..B16 (US-04) | → design: public endpoints |
| REQ-B17..B18 (US-05) | → design: halaman publik |
| REQ-B19..B22 (US-06) | → design: halaman admin |
| NFR-B01..B05 | → design: konfigurasi, validasi, seed |
