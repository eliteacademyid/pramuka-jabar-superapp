# Super Apps Pramuka Jawa Barat - API Backend

Aplikasi manajemen program dan kegiatan Pramuka Jawa Barat dengan sistem autentikasi JWT, CRUD operations, search, filtering, pagination, dan dokumentasi API Swagger.

## 📋 Fitur Utama

### ✅ Autentikasi & Keamanan
- ✓ Registrasi pengguna
- ✓ Login dengan username/email
- ✓ JWT Access Token & Refresh Token
- ✓ Password hashing dengan bcrypt
- ✓ Role-based access control (Admin/Staff)
- ✓ Protected endpoints dengan JWT middleware

### ✅ Manajemen Data
- ✓ **Organisasi**: CRUD operations
- ✓ **Program**: CRUD + Search + Filter (tahun, status) + Pagination + Sorting
- ✓ **Kegiatan**: CRUD + Search + Filter (program, status, date) + Pagination

### ✅ API Documentation
- ✓ Swagger UI auto-generated (`/docs`)
- ✓ ReDoc documentation (`/redoc`)
- ✓ OpenAPI schema (`/openapi.json`)

### ✅ Database
- ✓ PostgreSQL dengan SQLAlchemy ORM
- ✓ Alembic migrations
- ✓ Relational models dengan foreign keys
- ✓ Automatic timestamps (created_at, updated_at)

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- pip atau poetry

### 1. Virtual Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan kredensial database Anda
nano .env
```

**Konfigurasi .env:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/db_pramuka_jabar
SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb db_pramuka_jabar

# Run migrations
alembic upgrade head
```

### 5. Seed Default Data

Default data akan di-seed otomatis saat aplikasi startup:
- Admin Role
- Staff Role
- Default Admin User (username: `admin`, password: `admin123`)

---

## 🏃 Running the Application

### Development Server

```bash
cd backend
source venv/bin/activate

# Run with uvicorn (development)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
# Run with multiple workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📚 API Documentation

Setelah aplikasi berjalan, akses dokumentasi:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🔐 Authentication Flow

### 1. Register User

```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "nama_lengkap": "Nama Lengkap User",
  "password": "secure_password"
}
```

### 2. Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username_or_email": "user123",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Use Access Token

Tambahkan header pada setiap request:
```
Authorization: Bearer {access_token}
```

### 4. Refresh Token

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

---

## 📋 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register pengguna baru |
| POST | `/api/auth/login` | Login pengguna |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get user info |

### Organisasi
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/organisasi` | Get all organisasi |
| GET | `/api/organisasi/{id}` | Get organisasi by ID |
| POST | `/api/organisasi` | Create organisasi (admin) |
| PUT | `/api/organisasi/{id}` | Update organisasi (admin) |
| DELETE | `/api/organisasi/{id}` | Delete organisasi (admin) |

### Program
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/programs?search=&tahun=&status=&skip=&limit=` | Get all programs (with filters) |
| GET | `/api/programs/{id}` | Get program by ID |
| POST | `/api/programs` | Create program |
| PUT | `/api/programs/{id}` | Update program |
| DELETE | `/api/programs/{id}` | Delete program |

**Query Parameters untuk Program:**
- `search`: Search by nama
- `tahun`: Filter by tahun
- `status`: Filter by status (active, inactive, archived)
- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 10, max: 100)
- `sort_by`: Sort field (created_at, nama, tahun)
- `order`: Sort order (asc, desc)

### Kegiatan
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/kegiatans?program_id=&status=&search=&skip=&limit=` | Get all kegiatans |
| GET | `/api/kegiatans/{id}` | Get kegiatan by ID |
| POST | `/api/kegiatans` | Create kegiatan |
| PUT | `/api/kegiatans/{id}` | Update kegiatan |
| DELETE | `/api/kegiatans/{id}` | Delete kegiatan |

**Query Parameters untuk Kegiatan:**
- `program_id`: Filter by program
- `status`: Filter by status
- `search`: Search by nama
- `skip`: Pagination offset
- `limit`: Items per page
- `sort_by`: Sort field
- `order`: Sort order

---

## 📦 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── auth.py              # Auth utilities (wrapper)
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection & session
│   ├── deps.py              # JWT dependencies
│   ├── main.py              # FastAPI app & routes
│   ├── models.py            # SQLAlchemy models
│   ├── seed.py              # Database seeding
│   ├── routers/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── organisasi.py    # Organisasi CRUD
│   │   ├── program.py       # Program CRUD
│   │   └── kegiatan.py      # Kegiatan CRUD
│   ├── schemas/
│   │   ├── user.py          # User schemas
│   │   ├── role.py          # Role schemas
│   │   ├── organisasi.py    # Organisasi schemas
│   │   ├── program.py       # Program schemas
│   │   └── kegiatan.py      # Kegiatan schemas
│   └── utils/
│       ├── password.py      # Password hashing
│       └── security.py      # JWT token generation
├── migrations/              # Alembic migrations
├── alembic.ini             # Alembic config
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
└── .gitignore

frontend/                   # (separate frontend app)
```

---

## 🗄️ Database Schema

### Tables
- **roles**: Administrator, Staff
- **users**: Pengguna sistem
- **organisasi**: Organisasi Pramuka
- **programs**: Program Pramuka
- **kegiatans**: Kegiatan dalam program

### Relationships
- User → Role (Many-to-One)
- User → Organisasi (Many-to-One)
- Program → User (creator) (Many-to-One)
- Program → Organisasi (Many-to-One)
- Kegiatan → Program (Many-to-One)

---

## 🔒 Security

- ✓ Password hashing dengan bcrypt
- ✓ JWT dengan experation time
- ✓ Refresh token untuk token renewal
- ✓ Role-based access control
- ✓ CORS middleware
- ✓ Database connection pooling

---

## 🧪 Testing

### Test Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "admin", "password": "admin123"}'
```

### Test Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer {access_token}"
```

---

## 📝 Migrasi Database

### Membuat Migration Baru

```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Deskripsi perubahan"
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1  # Rollback 1 revision
```

---

## 🐛 Troubleshooting

### Connection Error: Database tidak ditemukan
```bash
# Create database
createdb db_pramuka_jabar

# Run migrations
alembic upgrade head
```

### JWT Token Error
- Pastikan SECRET_KEY di .env sudah di-set
- Pastikan token di-include di header: `Authorization: Bearer {token}`

### CORS Error
- CORS sudah dikonfigurasi untuk semua origin ("*")
- Ubah di `app/main.py` jika ingin membatasi origin

---

## 📞 Support & Contribution

Untuk issues atau suggestions, silakan buat issue di repository.

---

## 📄 License

MIT License - Pramuka Jawa Barat

---

**Terbuat dengan ❤️ untuk Pramuka Jawa Barat**
