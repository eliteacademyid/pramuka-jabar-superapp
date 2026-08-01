# Super Apps Pramuka Jawa Barat

Starter project "Super Apps Pramuka Jawa Barat" — fondasi aplikasi kepramukaan
sebelum fitur-fitur lain dikembangkan. Saat ini mencakup landing page publik,
login admin, dashboard admin, dan manajemen user (CRUD).

## Tech Stack

- **Frontend**: Vue 3 (Composition API), Vite, vue-router, axios
- **Backend**: FastAPI, SQLAlchemy
- **Database**: PostgreSQL (`db_pramuka_jabar`)

## Struktur

```
.
├── backend/    # FastAPI + SQLAlchemy
└── frontend/   # Vue 3 + Vite
```

## Prasyarat

- Node.js >= 18 dan npm
- Python >= 3.9 dan pip
- PostgreSQL berjalan (port 5432)

## Instalasi & Menjalankan

### 1. Database

Buat database (sekali saja):

```bash
psql -U postgres -d postgres -c "CREATE DATABASE db_pramuka_jabar;"
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # sesuaikan value bila perlu
uvicorn app.main:app --reload
```

Backend jalan di `http://localhost:8000`. Saat pertama kali start, akun default
dibuat otomatis (hanya jika tabel user kosong).

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Buka `http://localhost:5173`.

## Akun Default

| Username | Password | Role  |
|----------|----------|-------|
| admin    | admin123 | admin |

> Ganti password akun admin sebelum dipakai di produksi.

## Endpoint API Utama

| Method | Path | Auth | Keterangan |
|--------|------|------|------------|
| POST | `/api/auth/login` | - | Login, return JWT |
| GET | `/api/auth/me` | ✅ | Data user yang login |
| GET | `/api/admin/users` | ✅ admin | List user |
| POST | `/api/admin/users` | ✅ admin | Tambah user |
| PUT | `/api/admin/users/{id}` | ✅ admin | Update user |
| DELETE | `/api/admin/users/{id}` | ✅ admin | Hapus user |

## Lisensi

Internal project — belum ditentukan.
