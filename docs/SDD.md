# Software Design Document (SDD)

**Super Apps Pramuka Jawa Barat**

| | |
|---|---|
| Nama Sistem | Super Apps Pramuka Jawa Barat |
| Versi Dokumen | 1.0 |
| Tanggal | 2 Agustus 2026 |
| Status | Draft |
| Repositori | `pramuka-jabar-superapp` |

---

## 1. Pendahuluan

### 1.1 Tujuan

Dokumen ini menjelaskan rancangan perangkat lunak "Super Apps Pramuka Jawa Barat" — aplikasi fondasi yang dikembangkan untuk organisasi Gerakan Pramuka Kwartir Daerah Jawa Barat. SDD ini menjadi acuan bagi pengembang untuk memahami arsitektur, desain data, desain API, desain antarmuka, serta rencana pengembangan fitur lanjutan.

### 1.2 Ruang Lingkup

Fitur yang tersedia pada versi awal (v1.0):

1. **Landing page publik** — halaman pengenalan aplikasi.
2. **Autentikasi admin** — login dengan JWT, logout.
3. **Dashboard admin** — ringkasan statistik data.
4. **Manajemen user (CRUD)** — tambah, lihat, ubah, hapus akun pengguna.

Fitur-fitur lain (berita, anggota, kegiatan, galeri, dokumen, pengaturan) direncanakan pada versi berikutnya dan sudah disediakan tempatnya pada menu sidebar (label "Segera Hadir").

### 1.3 Definisi dan Singkatan

| Istilah | Keterangan |
|---|---|
| SDD | Software Design Document |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| JWT | JSON Web Token |
| CRUD | Create, Read, Update, Delete |
| ORM | Object-Relational Mapping |
| SPA | Single Page Application |
| DB | Database (basis data) |

### 1.4 Referensi

- README aplikasi (`README.md`)
- Kode sumber `backend/` dan `frontend/`

---

## 2. Deskripsi Umum Sistem

### 2.1 Perspektif Sistem

Super Apps Pramuka Jawa Barat adalah aplikasi berbasis web berarsitektur **client-server** dengan pola **SPA + REST API**:

- **Frontend** berupa SPA (Vue 3) yang berjalan di browser.
- **Backend** berupa REST API (FastAPI) yang melayani autentikasi dan pengelolaan data.
- **Database** PostgreSQL menyimpan data pengguna secara persisten.

Frontend dan backend berkomunikasi melalui protokol HTTP/JSON. Pada lingkungan produksi, frontend disajikan oleh web server Nginx yang sekaligus berperan sebagai reverse proxy untuk permintaan `/api/*`.

### 2.2 Fungsi Utama

| Kode | Fungsi | Deskripsi |
|---|---|---|
| F-01 | Menampilkan landing page | Halaman publik pengenalan aplikasi. |
| F-02 | Login admin/staff | Autentikasi pengguna dengan username + password, menghasilkan token JWT. |
| F-03 | Melihat profil sendiri | Mendapatkan data pengguna yang sedang login. |
| F-04 | Logout | Menghapus token pada sisi klien. |
| F-05 | Melihat dashboard | Menampilkan ringkasan statistik (total user, berita, anggota, kegiatan). |
| F-06 | Melihat daftar user | Daftar seluruh akun pengguna. |
| F-07 | Menambah user | Membuat akun pengguna baru (admin). |
| F-08 | Mengubah user | Mengubah username, nama, password, role, status aktif (admin). |
| F-09 | Menghapus user | Menghapus akun pengguna (admin). |

### 2.3 Karakteristik Pengguna

| Role | Deskripsi | Hak Akses |
|---|---|---|
| Pengunjung | Publik, belum login | Landing page, halaman login |
| Admin | Pengelola sistem (Kwartir Daerah) | Semua fitur termasuk manajemen user |
| Staff | Staf organisasi | (diimplementasikan) seluruh fitur; belum dibedakan haknya selain `admin` |

Model role disimpan pada kolom `role` dengan nilai valid: `admin` dan `staff`. Guard otorisasi di sisi backend hanya membedakan akses khusus admin; role `staff` pada dasarnya mendapat akses yang sama kecuali fitur yang secara eksplisit membutuhkan `admin`.

### 2.4 Batasan Sistem

- Belum ada modul berita, anggota, kegiatan, galeri, dokumen, dan pengaturan (roadmap).
- Belum ada mekanisme registrasi mandiri; akun dibuat oleh admin.
- Belum ada pagination pada daftar user.
- Password default admin perlu diganti pada pemakaian produksi.

---

## 3. Arsitektur Sistem

### 3.1 Diagram Arsitektur

```
+---------------------+        HTTP/JSON         +---------------------+
|     Browser         |  ----------------------->|   Nginx (Frontend)  |
|  Vue 3 SPA (build)  |                          |  - static file SPA  |
+---------------------+                          |  - reverse proxy    |
                                                  |    /api -> backend  |
                                                  +----------+----------+
                                                             |
                                                  +----------v----------+
                                                  |  Backend (FastAPI)  |
                                                  |  - router auth      |
                                                  |  - router admin     |
                                                  |  - SQLAlchemy ORM   |
                                                  +----------+----------+
                                                             |
                                                 +-----------v-----------+
                                                 |  PostgreSQL 16        |
                                                 |  db_pramuka_jabar     |
                                                 +-----------------------+
```

Alur permintaan frontend → backend:

```
Browser -> GET / (HTML SPA)
Browser -> POST /api/auth/login  -> backend -> DB -> JWT
Browser -> GET /api/auth/me      -> backend (verifikasi JWT) -> DB -> user
Browser -> GET/POST/PUT/DELETE /api/admin/users -> backend (JWT + role admin) -> DB
```

### 3.2 Teknologi yang Digunakan

| Lapisan | Teknologi | Versi | Keterangan |
|---|---|---|---|
| Frontend | Vue 3 (Composition API) | 3.5 | Kerangka SPA |
| Frontend | Vite | 6.0 | Build tool & dev server |
| Frontend | vue-router | 4.5 | Routing SPA |
| Frontend | axios | 1.7 | HTTP client |
| Backend | FastAPI | 0.128 | Web framework |
| Backend | Uvicorn | 0.39 | ASGI server |
| Backend | SQLAlchemy | 2.0 | ORM |
| Backend | psycopg2-binary | 2.9 | Driver PostgreSQL |
| Backend | bcrypt | 4.2 | Hash password |
| Backend | python-jose | 3.4 | JWT sign/verify |
| Backend | python-dotenv | 1.1 | Baca file `.env` |
| Database | PostgreSQL | 16 | Basis data relasional |
| Infrastruktur | Docker / Podman Compose | - | Kontainerisasi (db, backend, frontend) |
| Web server | Nginx | 1.27 | Statis + reverse proxy |

### 3.3 Struktur Direktori

```
pramuka-jabar-superapp/
├── docker-compose.yml          # Orkestrasi kontainer (db, backend, frontend)
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example            # Template konfigurasi lingkungan
│   └── app/
│       ├── main.py             # Inisialisasi FastAPI, CORS, seed admin
│       ├── config.py           # Baca konfigurasi dari env
│       ├── database.py         # Engine & session SQLAlchemy
│       ├── models.py           # Model ORM (User)
│       ├── schemas.py          # Skema Pydantic (request/response)
│       ├── auth.py             # Hash & verifikasi password, JWT
│       ├── deps.py             # Dependency (get_current_user, get_current_admin)
│       ├── seed.py             # Seed admin default
│       └── routers/
│           ├── auth.py         # /api/auth/* (login, me)
│           └── admin.py        # /api/admin/users (CRUD)
└── frontend/
    ├── Dockerfile
    ├── nginx.conf              # Konfigurasi Nginx (SPA + proxy /api)
    ├── vite.config.js          # Proxy /api untuk dev server
    ├── index.html
    └── src/
        ├── main.js             # Bootstrap Vue
        ├── App.vue             # Komponen akar (router-view)
        ├── style.css           # Gaya global
        ├── router/index.js     # Definisi rute & guard autentikasi
        ├── services/api.js     # Instance axios + interceptor token
        ├── components/
        │   ├── PublicLayout.vue
        │   └── AdminLayout.vue
        └── views/
            ├── public/ (LandingPage, LoginPage)
            └── admin/  (Dashboard, Users)
```

### 3.4 Keputusan Desain Utama

1. **SPA + REST API**: pemisahan tegas frontend/backend memudahkan pengembangan paralel dan pemakaian API oleh klien lain (mis. aplikasi mobile).
2. **Reverse proxy Nginx**: frontend dan backend terlihat sebagai satu origin, menghindari masalah CORS pada produksi dan memudahkan konfigurasi domain.
3. **JWT stateless**: tidak perlu session server; token disimpan di `localStorage` browser.
4. **Hash password dengan bcrypt**: sandi tidak pernah disimpan sebagai teks polos.
5. **Seed admin otomatis**: akun admin awal dibuat otomatis saat pertama kali database kosong, memudahkan bootstrap.

---

## 4. Desain Basis Data

### 4.1 Entity Relationship Diagram

```
+----------------------+
|        users         |
+----------------------+
| PK id        int     |
|    username  string  |  UNIQUE, INDEX
|    hashed_password  |
|    nama_lengkap      |
|    role       string |  ('admin' | 'staff')
|    is_active boolean |
|    created_at datetime|
+----------------------+
```

Saat ini sistem hanya memiliki satu entitas: `users`. Entitas lain (berita, anggota, kegiatan, galeri, dokumen) belum ada dan akan ditambahkan pada pengembangan berikutnya.

### 4.2 Skema Tabel `users`

| Kolom | Tipe | Nullable | Default | Keterangan |
|---|---|---|---|---|
| `id` | INTEGER | No | autoincrement | Primary key |
| `username` | VARCHAR | No | - | Unique, diindex |
| `hashed_password` | VARCHAR | No | - | Hash bcrypt dari password |
| `nama_lengkap` | VARCHAR | No | - | Nama lengkap pengguna |
| `role` | VARCHAR | No | `staff` | Role: `admin` / `staff` |
| `is_active` | BOOLEAN | No | `true` | Status akun aktif |
| `created_at` | DATETIME | Yes | `utcnow` | Waktu pembuatan |

Catatan desain:

- Tabel dibuat otomatis melalui `Base.metadata.create_all()` pada startup aplikasi.
- Validasi nilai `role` dilakukan di lapisan aplikasi (`models.ROLES`).
- Akun dengan `is_active = false` tidak dapat login maupun memakai token.

### 4.3 Data Awal (Seed)

Saat tabel `users` kosong, pada event `startup` dibuat akun default:

| Username | Password | Nama | Role |
|---|---|---|---|
| admin | admin123 | Administrator | admin |

---

## 5. Desain API

### 5.1 Konvensi Umum

- Base path: `/api`
- Format data: JSON
- Autentikasi: `Authorization: Bearer <token>`
- Dokumentasi interaktif otomatis: `/docs` (Swagger UI) dan `/redoc` (Redoc)
- Format error standar FastAPI: `{"detail": "<pesan>"}`

### 5.2 Daftar Endpoint

| # | Method | Path | Auth | Role | Keterangan |
|---|---|---|---|---|---|
| 1 | POST | `/api/auth/login` | - | - | Login, mengembalikan token JWT |
| 2 | GET | `/api/auth/me` | ✅ | semua aktif | Data pengguna yang sedang login |
| 3 | GET | `/api/admin/users` | ✅ | admin | Daftar seluruh user |
| 4 | POST | `/api/admin/users` | ✅ | admin | Tambah user baru |
| 5 | PUT | `/api/admin/users/{id}` | ✅ | admin | Ubah data user |
| 6 | DELETE | `/api/admin/users/{id}` | ✅ | admin | Hapus user |
| 7 | GET | `/` | - | - | Health check sederhana |

### 5.3 Spesifikasi Request/Response

#### 5.3.1 POST `/api/auth/login`

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response 200:**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

**Error:** `401 {"detail": "Username atau password salah"}`, `401 {"detail": "Akun nonaktif"}`

#### 5.3.2 GET `/api/auth/me`

**Header:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": 1,
  "username": "admin",
  "nama_lengkap": "Administrator",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-08-02T12:00:00"
}
```

**Error:** `401` (token tidak valid / user tidak ditemukan / akun nonaktif)

#### 5.3.3 GET `/api/admin/users`

**Response 200:** array `UserOut` (urut berdasarkan id).

#### 5.3.4 POST `/api/admin/users`

**Request:**
```json
{
  "username": "joko",
  "password": "rahasia123",
  "nama_lengkap": "Joko Susilo",
  "role": "staff"
}
```

**Response 201:** objek `UserOut`.

**Error:** `400` (password < 6 karakter, role tidak valid, username sudah digunakan), `401`, `403`.

#### 5.3.5 PUT `/api/admin/users/{id}`

Semua field opsional; hanya field yang diisi yang diubah.

```json
{
  "username": "joko.s",
  "password": "baru123",
  "nama_lengkap": "Joko Susilo",
  "role": "staff",
  "is_active": false
}
```

**Response 200:** objek `UserOut`. **Error:** `404` (user tidak ditemukan), `400` (duplikat username / validasi), `403`.

#### 5.3.6 DELETE `/api/admin/users/{id}`

**Response 204** (tanpa body). **Error:** `400` (menghapus akun sendiri), `404`, `403`.

### 5.4 Alur Autentikasi (Sequence)

```
Client          Backend                     DB
  | POST /auth/login |                        |
  |----------------->|  query user            |
  |                  |----------------------->|
  |                  |  verifikasi bcrypt     |
  |                  |  buat JWT (exp 120m)   |
  |<---- token JWT --|                        |
  |                  |                        |
  | GET /admin/users |  validasi JWT          |
  | (Bearer token)-->|  + cek role == admin   |
  |                  |  query users           |
  |                  |----------------------->|
  |<---- list users -|                        |
```

### 5.5 Format Token JWT

- **Claims:** `sub` = username, `exp` = waktu kedaluwarsa (default 120 menit).
- **Algoritma:** HS256.
- **Secret:** `SECRET_KEY` dari environment.

---

## 6. Desain Frontend

### 6.1 Struktur Routing

| Path | Nama Route | Komponen | Layout | Guard |
|---|---|---|---|---|
| `/` | `landing` | LandingPage | PublicLayout | - |
| `/login` | `login` | LoginPage | PublicLayout | redirect ke dashboard bila sudah login |
| `/admin` | `admin-dashboard` | Dashboard | AdminLayout | `requiresAuth` |
| `/admin/users` | `admin-users` | Users | AdminLayout | `requiresAuth` |

**Guard autentikasi** (`router.beforeEach`):

1. Jika route membutuhkan auth (`meta.requiresAuth`) dan tidak ada token di `localStorage` → redirect ke `/login`.
2. Jika sudah ada token dan membuka `/login` → redirect ke `/admin`.

Catatan: pengecekan dilakukan hanya terhadap keberadaan token; validitas token diperiksa backend saat pemanggilan API (401 → logout pada `AdminLayout` / `Users`).

### 6.2 Komponen

| Komponen | Fungsi |
|---|---|
| `App.vue` | Akar aplikasi, menampilkan `router-view`. |
| `PublicLayout.vue` | Header brand + footer untuk halaman publik. |
| `AdminLayout.vue` | Sidebar (Dashboard, Manajemen User, menu "Segera Hadir"), info user, tombol logout; memuat `/auth/me` saat mount; logout bila gagal. |
| `LandingPage.vue` | Hero + tombol "Masuk". |
| `LoginPage.vue` | Form login, menyimpan token ke `localStorage`, redirect ke dashboard. |
| `Dashboard.vue` | Sapaan user + kartu statistik (Total User, Berita, Anggota, Kegiatan). |
| `Users.vue` | Tabel daftar user, modal tambah/edit, aksi hapus dengan konfirmasi. |

### 6.3 Komunikasi dengan Backend

`services/api.js` membuat instance axios dengan `baseURL: '/api'` dan interceptor request yang menambahkan header `Authorization: Bearer <token>` dari `localStorage`.

- **Produksi:** `/api` diproxy Nginx ke `backend:8000`.
- **Development:** `vite.config.js` mendefinisikan proxy `/api` → `http://localhost:8000`.

### 6.4 Penanganan Error

- Response error FastAPI dibaca dari `err.response.data.detail`.
- Pada halaman Users: status `401`/`403` memicu hapus token dan redirect ke login.
- Form login menampilkan pesan error langsung di bawah judul.

---

## 7. Desain Keamanan

| Aspek | Implementasi |
|---|---|
| Penyimpanan password | Hash bcrypt (`bcrypt.hashpw`), tidak pernah plaintext |
| Autentikasi | JWT (HS256) dengan `exp`, verifikasi di setiap endpoint privat |
| Otorisasi | Dependency `get_current_admin` memastikan role `admin`; selain admin → `403` |
| Akun nonaktif | Ditolak login maupun akses token (`is_active == false`) |
| Validasi input | Pydantic schema + validasi manual (panjang password, role, duplikat username) |
| CORS | `allow_origins=["*"]` — longgar untuk pengembangan; sebaiknya dipersempit untuk produksi |
| Secret key | Dibaca dari environment (`SECRET_KEY`); wajib diganti dari nilai default pada produksi |
| Proteksi aksi destruktif | Admin tidak dapat menghapus akun sendiri |

Rekomendasi produksi:

1. Ganti `SECRET_KEY` dan password admin default.
2. Persempit daftar `allow_origins` CORS.
3. Gunakan HTTPS di depan reverse proxy.
4. Pertimbangkan penyimpanan token di cookie `httpOnly` untuk keamanan XSS.

---

## 8. Deployment

### 8.1 Topologi Kontainer (Docker Compose)

| Service | Image / Build | Port Host | Keterangan |
|---|---|---|---|
| `db` | `postgres:16-alpine` | internal | Volume `pgdata` untuk persistensi |
| `backend` | build `./backend` | internal (`expose 8000`) | Hanya bisa diakses via frontend |
| `frontend` | build `./frontend` (nginx) | `8080:80` | Serve SPA + proxy `/api` |

`docker-compose.yml` menggunakan project name `pramuka-jabar` sehingga tidak bentrok dengan project lain di mesin yang sama.

### 8.2 Langkah Deploy

```bash
podman compose build
podman compose up -d
```

Aplikasi dapat diakses di `http://localhost:8080`.

### 8.3 Variabel Lingkungan Backend

| Variabel | Default | Keterangan |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres@localhost:5432/db_pramuka_jabar` | Koneksi database |
| `SECRET_KEY` | nilai bawaan (jangan dipakai di produksi) | Secret JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | Masa berlaku token (menit) |

---

## 9. Rencana Pengujian

### 9.1 Kasus Uji Fungsional (ringkasan)

| ID | Kasus | Langkah | Hasil Diharapkan |
|---|---|---|---|
| TC-01 | Login sukses | POST `/api/auth/login` admin/admin123 | 200 + token |
| TC-02 | Login gagal | password salah | 401 "Username atau password salah" |
| TC-03 | Login akun nonaktif | user `is_active=false` | 401 "Akun nonaktif" |
| TC-04 | Akses tanpa token | GET `/api/admin/users` | 401 |
| TC-05 | Akses non-admin | token user `staff` ke endpoint admin | 403 |
| TC-06 | Tambah user | POST valid | 201, muncul di daftar |
| TC-07 | Tambah username duplikat | POST username sama | 400 |
| TC-08 | Password pendek | < 6 karakter | 400 |
| TC-09 | Ubah user | PUT `/api/admin/users/2` | 200, data berubah |
| TC-10 | Hapus user | DELETE `/api/admin/users/2` | 204 |
| TC-11 | Hapus akun sendiri | DELETE id sendiri | 400 |
| TC-12 | Guard frontend | Buka `/admin` tanpa token | redirect `/login` |
| TC-13 | Logout | klik Logout | token terhapus, kembali ke landing |

### 9.2 Peralatan yang Diusulkan

- **Backend:** pytest + httpx TestClient (FastAPI TestClient).
- **Frontend:** Vitest + Vue Test Utils.
- **E2E:** Playwright (opsional).
- **API manual:** Swagger UI `/docs`.

---

## 10. Rencana Pengembangan Lanjutan (Roadmap)

| Prioritas | Fitur | Catatan |
|---|---|---|
| 1 | Modul Berita | CRUD berita, kategori, publish status |
| 2 | Modul Anggota | Data anggota pramuka (identitas, gugus depan, pangkalan) |
| 3 | Modul Kegiatan | Agenda/jadwal kegiatan, pendaftaran |
| 4 | Modul Galeri | Unggah foto/video kegiatan |
| 5 | Modul Dokumen | Penyimpanan & berbagi dokumen resmi |
| 6 | Modul Pengaturan | Konfigurasi aplikasi dan profil organisasi |
| 7 | Pagination & pencarian | Untuk daftar data berskala besar |
| 8 | Role & permission detail | Pemisahan hak akses `admin` vs `staff` yang lebih rinci |
| 9 | Audit log | Catatan aktivitas pengguna |
| 10 | Notifikasi | Pemberitahuan kegiatan/informasi |

---

## 11. Lampiran

### 11.1 Konfigurasi Nginx (`frontend/nginx.conf`)

- Serve static file dari `/usr/share/nginx/html` (hasil build Vite).
- `/api/*` di-proxy ke `http://backend:8000`.
- Fallback SPA: semua path selain `/api` diarahkan ke `index.html`.

### 11.2 Perintah Operasional

| Tujuan | Perintah |
|---|---|
| Mulai/restart semua service | `podman compose up -d` |
| Lihat log | `podman compose logs -f` |
| Hentikan service | `podman compose down` (data DB tetap aman di volume) |
| Build ulang image | `podman compose build` |
