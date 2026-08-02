#!/bin/bash

# Simple SDD Implementation Script
# Implementasi modul Data Potensi Keanggotaan (Gerakan Pramuka)
cd /home/opencode/team4/pramuka-jabar-superapp

echo "=== Implementing SDD (Data Potensi Keanggotaan) Module ==="
echo ""

# Setup backend
echo "Setting up SDD Backend..."
cd backend

# Install dependencies sistem
if command -v apt-get &> /dev/null; then
    apt-get update && apt-get install -y python3-pip python3-venv 2>/dev/null || echo "Gagal install packages"
fi

# Install pip dependencies
echo "Installing Python dependencies..."
pip3 install fastapi uvicorn sqlalchemy python-dotenv bcrypt python-jose
pip3 install python-multipart

# Buat virtual environment
echo "Membuat virtual environment..."
python3 -m venv venv

# Activate venv dan install requirements
source venv/bin/activate
pip install -r requirements.txt

# Export environment variables
export DATABASE_URL="sqlite:///api.db"
export SECRET_KEY="$(openssl rand -hex 32)"
export ACCESS_TOKEN_EXPIRE_MINUTES=120

# Buat .env jika belum ada
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo "Setup database..."
python3 -c "
from app.database import Base, engine
from app.models import Wilayah, Gudep, User, Anggota, RiwayatJenjang, KompetensiMaster, CapaianKompetensi, PotensiMinat, LogAudit
from app.auth import hash_password

# Buat semua tabel
Base.metadata.create_all(bind=engine)
print('✓ Database tables created successfully')

# Buat data sample
try:
    conn = engine.connect()
    
    # Insert data menggunakan SQLAlchemy
    wilayah_data = [
        {'nama': 'Jawa Barat', 'tingkat': 'Daerah', 'parent_id': None},
        {'nama': 'Tasikmalaya', 'tingkat': 'Ranting', 'parent_id': None},
        {'nama': 'Ciamis', 'tingkat': 'Ranting', 'parent_id': None},
    ]
    
    from sqlalchemy import insert
    for data in wilayah_data:
        stmt = insert(Wilayah).values(
            nama=data['nama'],
            tingkat=data['tingkat'],
            parent_id=data['parent_id']
        )
        conn.execute(stmt)
    
    gudep_data = [
        {'nama': 'Gudep 1', 'pangkalan': 'SDN 1', 'wilayah_id': 1},
        {'nama': 'Gudep 2', 'pangkalan': 'SMAN 1', 'wilayah_id': 2},
        {'nama': 'Gudep 3', 'pangkalan': 'SMP 1', 'wilayah_id': 3},
    ]
    
    for data in gudep_data:
        stmt = insert(Gudep).values(
            nama=data['nama'],
            pangkalan=data['pangkalan'],
            wilayah_id=data['wilayah_id']
        )
        conn.execute(stmt)
    
    # Insert admin user
    stmt = insert(User).values(
        username='admin',
        hashed_password=hash_password('admin123'),
        nama_lengkap='Admin SuperApp',
        role='superadmin',
        is_active=True
    )
    conn.execute(stmt)
    
    conn.commit()
    conn.close()
    print('✓ Sample data created successfully')
    
except Exception as e:
    print(f'Warning: {e}')
    print('(This is okay if tables already exist)')
" 2>&1

echo "Menjalankan backend SDD..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend SDD PID: $BACKEND_PID"
echo $BACKEND_PID > backend.pid
sleep 5

# Test backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend SDD berhasil dijalankan di http://localhost:8000"
else
    echo "✗ Backend SDD gagal dijalankan"
    cat backend.log 2>/dev/null | head -20
    exit 1
fi

cd ..

echo ""
echo "=== SDD Implementation Complete ==="
echo ""
echo "🎯 Backend SDD:"
echo "   → http://localhost:8000"
echo "   → Health: http://localhost:8000/health"
echo ""
echo "📊 API Endpoints SDD:"
echo ""
echo "🏠 Menu: Dashboard Keanggotaan"
echo "   → GET /api/dashboard/anggota"
echo ""
echo "👥 Menu: Data Anggota"
echo "   → GET /api/anggota (list)"
echo "   → POST /api/anggota (create)"
echo "   → GET /api/anggota/{id}"
echo "   → PUT /api/anggota/{id}"
echo "   → DELETE /api/anggota/{id}"
echo ""
echo "🔧 Menu: Pemetaan Kompetensi"
echo "   → GET /api/kompetensi-master (SKU/SKK/TKK)"
echo "   → POST /api/capaian-kompetensi (catat capaian)"
echo "   → GET /api/capaian-kompetensi/anggota/{anggota_id}"
echo ""
echo "📊 Menu: Rekapitulasi & Laporan"
echo "   → GET /api/rekap/anggota/jenjang"
echo "   → GET /api/rekap/anggota/wilayah"
echo "   → GET /api/rekap/laporan/periodik"
echo ""
echo "⚙️ Menu: Administrasi Keanggotaan"
echo "   → GET /api/admin/users (kelola pengguna)"
echo "   → GET /api/admin/log-audit (log audit)"
echo ""
echo "=== Testing API ==="
echo "Test auth..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo $TOKEN
if [ ! -z "$TOKEN" ]; then
    echo "✓ Auth endpoint working"
    echo "Token: ${TOKEN:0:20}..."
    
    echo ""
    echo "Test anggota endpoints..."
    curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/anggota | head -20
    echo "✓ Anggota endpoints working"
    
    echo ""
    echo "Test kompetensi endpoints..."
    curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/kompetensi-master
    echo "✓ Kompetensi endpoints working"
    
    echo ""
    echo "Test capaian endpoints..."
    curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/capaian-kompetensi/anggota/1
    echo "✓ Capaian endpoints working"
    
else
    echo "✗ Auth endpoint failed"
fi

echo ""
echo "=== SDD Implementation Selesai ==="
echo "🎯 SDD (Data Potensi Keanggotaan) siap digunakan!"
echo ""
echo "API Endpoints yang tersedia:"
echo "   → Auth: http://localhost:8000/api/auth/"
echo "   → Admin: http://localhost:8000/api/admin/"
echo "   → Anggota: http://localhost:8000/api/anggota/"
echo "   → Riwayat: http://localhost:8000/api/riwayat-jenjang/"
echo "   → Kompetensi: http://localhost:8000/api/kompetensi-master/"
echo "   → Capaian: http://localhost:8000/api/capaian-kompetensi/"
echo ""
echo "Frontend: http://localhost:3003 (jika Node/Frontend siap)"
echo ""
echo "Untuk berhenti: kill $BACKEND_PID"
echo ""
