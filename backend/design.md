# Design Document

## Modul: Data Potensi Keanggotaan (Gerakan Pramuka)

### Konteks: Sub-modul dari **Kwarda SuperApp**

Modul ini **tidak berdiri sendiri** sebagai aplikasi terpisah, melainkan menjadi salah satu **sub-menu/modul** di dalam **Kwarda SuperApp** — platform terpadu Kwartir Daerah yang menaungi banyak modul lain (mis. Kegiatan, Keuangan/Iuran, Presensi, Persuratan, Perizinan, dsb). Implikasinya terhadap desain:

- **Satu pintu masuk (single sign-on)**: login, sesi, dan RBAC dikelola oleh **Core/Platform SuperApp**, bukan oleh modul ini sendiri. Modul Data Potensi Keanggotaan cukup mengonsumsi token & peran dari Core.
- **Master data dipakai bersama (shared)**: entitas `wilayah` (Kwarran/Kwarcab/Kwarda/Kwarnas) dan `gudep` idealnya adalah **master data milik Core SuperApp**, direferensikan (foreign key/API) oleh modul ini, bukan diduplikasi.
- **Menu bersarang (nested submenu)**: menu-menu modul ini (Dashboard, Data Anggota, Pemetaan Kompetensi, dst.) tampil sebagai **submenu di bawah grup menu "Keanggotaan"** pada navigasi utama SuperApp, bersanding dengan grup menu modul lain.
- **Modularitas backend**: disarankan pendekatan **modular monolith** atau **microservice per domain** dengan API Gateway di depan, sehingga modul ini bisa dikembangkan/dideploy relatif independen namun tetap satu ekosistem.

## 1. Ikhtisar Arsitektur (dalam konteks SuperApp)

Aplikasi menggunakan arsitektur **3-tier** berbasis web:

```
┌───────────────────────────────────────────────────────────┐
│                 Client SuperApp (Browser/PWA)              │
│   Shell/Layout SuperApp ─ Menu Utama (semua modul)          │
│      └── Submenu "Keanggotaan" ← modul ini dirender di sini │
└───────────────────────────┬─────────────────────────────────┘
                             │ HTTPS/REST (JSON)
┌───────────────────────────▼─────────────────────────────────┐
│                    API Gateway SuperApp                       │
│   - Autentikasi SSO & penerbitan token (Core Auth Service)   │
│   - Routing ke masing-masing modul/service                   │
└───────┬───────────────┬───────────────┬──────────────────────┘
        │               │               │
┌───────▼──────┐ ┌──────▼───────────┐ ┌─▼───────────────┐
│ Core Service │ │ Modul Keanggotaan│ │ Modul Lain       │
│ (User, RBAC, │ │ (Data Potensi    │ │ (Kegiatan,       │
│  Wilayah,    │ │  Keanggotaan)    │ │  Keuangan, dll)  │
│  Gudep)      │ │  - service ini   │ │                  │
└───────┬──────┘ └──────┬───────────┘ └──────────────────┘
        │               │
┌───────▼───────────────▼──────────────────────────────────────┐
│        Database (PostgreSQL, shared schema/service DB)         │
│        + Object Storage (S3) untuk foto & dokumen               │
└─────────────────────────────────────────────────────────────────┘
```

**Tumpukan teknologi yang disarankan (selaras dengan SuperApp existing):**

- Frontend: mengikuti framework shell SuperApp yang sudah ada (React/Vue), modul ini dibangun sebagai **micro-frontend/module route** (mis. `/keanggotaan/*`), bukan aplikasi terpisah dengan layout sendiri.
- Backend: Node.js (Express/NestJS) atau Laravel — REST API sebagai **service/modul** di balik API Gateway SuperApp.
- Database: PostgreSQL — skema `keanggotaan` terpisah namun tetap dalam satu instance/cluster database SuperApp bila memungkinkan (memudahkan join lintas modul, mis. Keuangan/Iuran per anggota).
- Autentikasi: **didelegasikan ke Core Auth Service SuperApp** (SSO, JWT terbit dari sana); modul ini hanya memvalidasi token & membaca klaim peran/wilayah.
- Penyimpanan berkas: S3-compatible object storage bersama (bucket/prefix khusus modul ini) untuk foto & sertifikat.
- Job scheduler: cron/queue (mis. Bull/Redis) untuk rekap berkala & notifikasi kenaikan tingkat, terintegrasi dengan sistem notifikasi SuperApp jika sudah ada (agar tidak membangun channel notifikasi baru).

---

## 2. Struktur Menu — Posisi dalam Navigasi Kwarda SuperApp

Menu SuperApp bersifat **satu shell navigasi global**, dan modul ini muncul sebagai **satu grup menu ("Keanggotaan")** berisi submenu-submenu di bawahnya — bersanding dengan grup-grup menu modul lain milik SuperApp.

```
KWARDA SUPERAPP (Menu Utama)
│
├── 🏠 Dashboard SuperApp (ringkasan lintas modul)
│
├── 👥 Keanggotaan  ◄── GRUP MENU MODUL INI (Data Potensi Keanggotaan)
│   ├── Dashboard Keanggotaan
│   │   ├── Ringkasan Jumlah Anggota (per jenjang & wilayah)
│   │   └── Grafik Tren Pertumbuhan Anggota
│   │
│   ├── Data Anggota
│   │   ├── Siaga
│   │   ├── Penggalang
│   │   ├── Penegak
│   │   ├── Pandega
│   │   ├── Anggota Dewasa
│   │   ├── Tambah Anggota Baru
│   │   └── Impor Data (Excel)
│   │
│   ├── Pemetaan Kompetensi
│   │   ├── Capaian SKU/SKK/TKK
│   │   ├── Potensi & Minat/Bakat
│   │   ├── Profil Kompetensi Individu (radar chart)
│   │   └── Rekap Kompetensi per Gudep
│   │
│   ├── Rekapitulasi & Laporan
│   │   ├── Rekap per Jenjang
│   │   ├── Rekap per Wilayah (Gudep/Kwarran/Kwarcab/Kwarda)
│   │   ├── Laporan Periodik (Bulanan/Tahunan)
│   │   └── Ekspor Laporan (PDF/Excel)
│   │
│   └── Administrasi Keanggotaan
│       ├── Master Data SKU/SKK/TKK
│       └── Log Audit Keanggotaan

**Catatan integrasi penting:**
- Menu **"Manajemen Pengguna & Hak Akses"** dan **"Master Data Wilayah/Gudep"** dipindahkan ke level **Administrasi SuperApp (Core)**, karena dipakai bersama oleh semua modul — modul Keanggotaan hanya menyisakan **"Master Data SKU/SKK/TKK"** dan **"Log Audit"** miliknya sendiri di bawah "Administrasi Keanggotaan".
- Menu bersifat **dinamis berbasis peran (role-based menu rendering)** dari Core SuperApp: grup "Keanggotaan" hanya tampil bila peran pengguna memiliki hak akses ke modul ini; submenu "Administrasi Keanggotaan" hanya tampil untuk Super Admin/Admin Kwartir.
- **"Profil Saya" → "Riwayat Jenjang"** adalah contoh titik integrasi: halaman ini milik Core, tapi datanya diambil (via internal API) dari modul Keanggotaan — pola serupa dapat dipakai modul lain (mis. modul Keuangan menampilkan status iuran per anggota dengan menarik data dasar anggota dari modul ini).
- Breadcrumb mengikuti hierarki penuh, contoh: `SuperApp / Keanggotaan / Data Anggota / Penggalang / Detail Anggota`.

---

## 3. Model Data (Entity Relationship)

> **Kepemilikan data dalam konteks SuperApp:**
> - Entitas **`wilayah`**, **`gudep`**, dan **`pengguna`** berstatus **shared/milik Core SuperApp** — modul ini hanya mereferensikan (FK/API), tidak menduplikasi atau menjadi sumber kebenaran (source of truth).
> - Entitas **`anggota`, `riwayat_jenjang`, `kompetensi_master`, `capaian_kompetensi`, `potensi_minat`** adalah **milik/domain modul Keanggotaan** ini.
> - `log_audit` dapat berupa skema per-modul yang mengalir ke **log audit terpusat SuperApp** (event streaming) atau langsung memakai tabel audit Core — dipilih sesuai standar SuperApp yang sudah berjalan.

### Entitas Utama

**anggota**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID (PK) | |
| nta | varchar unique | Nomor Tanda Anggota |
| nama_lengkap | varchar | |
| tanggal_lahir | date | |
| jenis_kelamin | enum(L,P) | |
| jenjang | enum(Siaga,Penggalang,Penegak,Pandega,Dewasa) | |
| gudep_id | UUID (FK → gudep) | |
| status_aktif | boolean | |
| foto_url | varchar | |
| kontak | jsonb | telepon, email, alamat |
| created_at / updated_at | timestamp | |

**gudep** *(referensi ke Core — read-only dari sisi modul ini)*
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | UUID (PK) | |
| nama_gudep | varchar | |
| pangkalan | varchar | sekolah/komunitas |
| kwarran_id | UUID (FK → wilayah) | |

**wilayah** *(referensi ke Core — read-only dari sisi modul ini)* — self-referencing untuk hierarki Kwarran→Kwarcab→Kwarda→Kwarnas
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| nama | varchar |
| tingkat | enum(Ranting,Cabang,Daerah,Nasional) |
| parent_id | UUID (FK → wilayah, nullable) |

**riwayat_jenjang**
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| anggota_id | UUID (FK) |
| jenjang_lama | enum |
| jenjang_baru | enum |
| tanggal_mutasi | date |

**kompetensi_master** (daftar SKU/SKK/TKK)
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| jenis | enum(SKU,SKK,TKK) |
| jenjang | enum | jenjang yang berlaku |
| nama_kompetensi | varchar |
| tingkat | varchar | mis. Mula/Bantu/Tata |

**capaian_kompetensi**
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| anggota_id | UUID (FK) |
| kompetensi_id | UUID (FK → kompetensi_master) |
| tanggal_capai | date |
| penguji_id | UUID (FK → anggota, Pembina) |

**potensi_minat**
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| anggota_id | UUID (FK) |
| kategori | varchar | seni/olahraga/teknologi/kepemimpinan/dll |
| deskripsi | text |

**pengguna** *(dikelola oleh Core Auth Service SuperApp — modul ini hanya membaca klaim dari token)*
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| anggota_id | UUID (FK, nullable) |
| username | varchar unique |
| password_hash | varchar |
| role | enum(SuperAdmin,AdminKwartir,AdminGudep,Pembina,Anggota) |
| wilayah_scope_id | UUID (FK → wilayah, nullable) |

**log_audit**
| Kolom | Tipe |
|---|---|
| id | UUID (PK) |
| pengguna_id | UUID (FK) |
| aksi | varchar |
| entitas | varchar |
| entitas_id | UUID |
| detail | jsonb |
| waktu | timestamp |

### Diagram Relasi (ringkas)
```

wilayah (1)───(N) gudep (1)───(N) anggota (1)───(N) riwayat_jenjang
│
├──(N) capaian_kompetensi ──(N:1) kompetensi_master
├──(N) potensi_minat
└──(1:1, opsional) pengguna

```

---

## 4. Desain API (contoh endpoint utama)

| Method | Endpoint | Deskripsi | Role |
|---|---|---|---|
| POST | /api/auth/login | Login pengguna | Semua |
| GET | /api/anggota?jenjang=&wilayah=&q= | Cari/filter anggota | Semua (scoped) |
| POST | /api/anggota | Tambah anggota baru | AdminGudep+ |
| PUT | /api/anggota/:id | Perbarui profil anggota | AdminGudep+ |
| POST | /api/anggota/:id/mutasi-jenjang | Naik/mutasi jenjang | Pembina/AdminGudep |
| POST | /api/anggota/import | Impor data massal (Excel) | AdminGudep+ |
| GET | /api/kompetensi/master?jenjang= | Daftar master SKU/SKK/TKK | Semua |
| POST | /api/anggota/:id/capaian | Catat capaian kompetensi | Pembina |
| POST | /api/anggota/:id/potensi | Catat potensi/minat | Pembina/Anggota |
| GET | /api/rekap/jenjang?wilayah= | Rekap jumlah per jenjang | AdminKwartir+ |
| GET | /api/rekap/laporan?periode= | Laporan periodik | AdminKwartir+ |
| GET | /api/rekap/export?format=pdf|xlsx | Ekspor laporan | AdminKwartir+ |
| GET/POST | /api/admin/users | Kelola pengguna & role | SuperAdmin |
| GET | /api/admin/log-audit | Lihat log audit | SuperAdmin |

Semua endpoint (kecuali login) memerlukan header `Authorization: Bearer <JWT>` dan melalui middleware RBAC + data-scoping wilayah.

---

## 5. Alur Utama (Sequence Ringkas)

**Alur pencatatan capaian kompetensi:**
1. Pembina login → membuka menu "Pemetaan Kompetensi".
2. Sistem menampilkan daftar anggota binaan Pembina (scoped by gudep).
3. Pembina memilih anggota → memilih SKU/SKK yang dicapai → submit.
4. API memvalidasi kompetensi sesuai jenjang anggota → simpan `capaian_kompetensi`.
5. Sistem mengecek apakah seluruh SKU tingkat tersebut sudah lengkap → jika ya, set status "siap naik tingkat" dan kirim notifikasi ke Pembina.

**Alur rekapitulasi Admin Kwartir:**
1. Admin Kwartir login → buka menu "Rekapitulasi & Laporan".
2. Pilih cakupan wilayah (otomatis dibatasi sesuai `wilayah_scope_id` akun).
3. API mengagregasi data anggota via query wilayah rekursif (CTE) → gudep → anggota.
4. Sistem menampilkan dashboard grafik + tabel, dengan opsi ekspor PDF/Excel.

---

## 6. Keamanan & Kontrol Akses
- **RBAC** dengan 5 peran utama; setiap request API di-scope berdasarkan `wilayah_scope_id`/`gudep_id` pengguna.
- Data sensitif anak (di bawah 18 tahun) dienkripsi di database (kolom kontak/alamat) dan akses foto melalui signed URL sementara.
- Password di-hash menggunakan bcrypt/argon2; sesi menggunakan JWT short-lived + refresh token.
- Rate limiting pada endpoint login & impor data untuk mencegah abuse.
- Log audit mencatat setiap create/update/delete pada entitas `anggota`, `capaian_kompetensi`, dan `pengguna`.

## 7. Pertimbangan Desain UI
- Warna & ikon berbeda per jenjang untuk memudahkan identifikasi visual (mis. Siaga = kuning/hijau, Penggalang = merah, Penegak/Pandega = kuning tua/cokelat) sesuai konvensi seragam Pramuka, digunakan hanya sebagai aksen tabel/badge, bukan logo resmi.
- Tabel data anggota mendukung pagination, sorting, dan filter kolom.
- Radar chart digunakan untuk memvisualisasikan profil kompetensi individu (sumbu: jenis kecakapan/kategori potensi).
- Mobile-first untuk Pembina yang sering menginput data di lapangan.
```
