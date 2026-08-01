# 🚀 Quick Start Guide - Pramuka Jawa Barat API

## ⚡ Get Running in 5 Minutes

### Step 1: Setup Environment
```bash
cd /home/raka/MyKoding/pramuka-jabar-superapp
source venv/bin/activate
cd backend
```

### Step 2: Setup Database
```bash
# Create PostgreSQL database
createdb db_pramuka_jabar

# Run migrations to create tables
alembic upgrade head
```

### Step 3: Run the API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Access the API
- **API Base**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔐 Login & Get Started

### 1. Login with Default Admin
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Use Access Token for Protected Routes
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📝 Common API Operations

### Create Organization
```bash
curl -X POST http://localhost:8000/api/organisasi \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Pramuka Kota Bandung",
    "alamat": "Jl. Merdeka 123",
    "telepon": "+62812345678",
    "email": "pramuka.bandung@example.com"
  }'
```

### Create Program
```bash
curl -X POST http://localhost:8000/api/programs \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Program Pembinaan Pemimpin Tingkat Lanjut",
    "deskripsi": "Program pelatihan kepemimpinan untuk anggota senior",
    "tahun": 2024,
    "status": "active",
    "organisasi_id": 1
  }'
```

### Create Kegiatan
```bash
curl -X POST http://localhost:8000/api/kegiatans \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nama": "Latihan Dasar Kepemimpinan",
    "deskripsi": "Pelatihan LDK untuk penggemblengan pemimpin",
    "program_id": 1,
    "tanggal_mulai": "2024-08-15T08:00:00",
    "tanggal_selesai": "2024-08-20T17:00:00",
    "lokasi": "Kampus Universitas Padjadjaran",
    "status": "active"
  }'
```

### Get Programs with Filter & Search
```bash
# Search by name
curl "http://localhost:8000/api/programs?search=Pembinaan" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by year
curl "http://localhost:8000/api/programs?tahun=2024" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by status with pagination
curl "http://localhost:8000/api/programs?status=active&skip=0&limit=10&sort_by=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Kegiatans for a Program
```bash
curl "http://localhost:8000/api/kegiatans?program_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Available Query Parameters

### Program Endpoints
- `search` - Search by program name
- `tahun` - Filter by year
- `status` - Filter by status (active, inactive, archived)
- `skip` - Pagination offset (default: 0)
- `limit` - Items per page (default: 10, max: 100)
- `sort_by` - Sort by field (created_at, nama, tahun)
- `order` - Sort direction (asc, desc)

### Kegiatan Endpoints
- `program_id` - Filter by program ID
- `status` - Filter by status (active, inactive, completed)
- `search` - Search by kegiatan name
- `skip` - Pagination offset
- `limit` - Items per page
- `sort_by` - Sort by field (created_at, nama, tanggal_mulai)
- `order` - Sort direction

---

## 🔑 All Available Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Organisasi (Admin Only)
- `GET /api/organisasi` - List all
- `GET /api/organisasi/{id}` - Get one
- `POST /api/organisasi` - Create
- `PUT /api/organisasi/{id}` - Update
- `DELETE /api/organisasi/{id}` - Delete

### Programs
- `GET /api/programs` - List with filters
- `GET /api/programs/{id}` - Get one
- `POST /api/programs` - Create
- `PUT /api/programs/{id}` - Update
- `DELETE /api/programs/{id}` - Delete

### Kegiatans
- `GET /api/kegiatans` - List with filters
- `GET /api/kegiatans/{id}` - Get one
- `POST /api/kegiatans` - Create
- `PUT /api/kegiatans/{id}` - Update
- `DELETE /api/kegiatans/{id}` - Delete

### Admin (Admin Only)
- `GET /api/admin/users` - List users
- `GET /api/admin/users/{id}` - Get user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/roles` - List roles
- `POST /api/admin/roles` - Create role

---

## 🧪 Testing with Swagger

1. Go to: http://localhost:8000/docs
2. Click on **Authorize** button
3. Enter your access token
4. Try any endpoint directly from the UI!

---

## ⚙️ Configuration

Edit `backend/.env` to change:
```
DATABASE_URL=postgresql://user:password@localhost:5432/db_pramuka_jabar
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🐛 Troubleshooting

**"Connection refused" error:**
- Check PostgreSQL is running: `psql -l`
- Check DATABASE_URL in .env

**"Token invalid" error:**
- Make sure token was copied completely
- Check header format: `Authorization: Bearer token_here`
- Token might have expired - get a new one

**Port 8000 already in use:**
- Use different port: `uvicorn app.main:app --port 8001`

---

## 📖 Full Documentation

- Read [backend/README.md](backend/README.md) for complete documentation
- Read [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) for project status

---

**Status: 🚀 Ready to Use!**
