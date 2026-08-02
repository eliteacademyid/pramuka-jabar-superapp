#!/bin/bash

# Simple deployment for Pramuka Jabar Superapp
# Backend: http://localhost:8000
# Frontend: http://localhost:3004 (APP4_PORT)

cd /home/opencode/team4/pramuka-jabar-superapp

echo "=== Deploying Pramuka Jabar Superapp ==="
echo "Frontend akan tersedia di: http://localhost:3004"
echo ""

# Setup backend
echo "Setting up backend..."
cd backend

# Install python dependencies globally if venv fails
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv 2>/dev/null || python3 -m pip install --user virtualenv && virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Export environment variables
# Gunakan SQLite sebagai fallback jika PostgreSQL tidak tersedia
if pg_isready -q 2>/dev/null; then
    export DATABASE_URL="${DATABASE_URL:-postgresql://postgres@localhost:5432/db_pramuka_jabar}"
    echo "Database: PostgreSQL"
else
    export DATABASE_URL="sqlite:///api.db"
    echo "Database: SQLite (fallback)"
fi

export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
export ACCESS_TOKEN_EXPIRE_MINUTES=120

# Buat .env jika belum ada
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Menjalankan backend di port 8000
if [ -f "backend.pid" ] && kill -0 "$(cat backend.pid)" 2>/dev/null; then
    echo "Backend sudah berjalan (PID: $(cat backend.pid))."
else
    echo "Menjalankan backend di http://localhost:8000"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    echo $BACKEND_PID > backend.pid
    sleep 3
fi

cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend

# Build frontend (memerlukan npm)
if command -v npm &> /dev/null; then
    echo "Mem-build frontend..."
    npm run build
else
    echo "npm tidak ditemukan. Membuat frontend.json statis..."
    cat > dist/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Pramuka Jabar Superapp</title>
</head>
<body>
    <div id="app">
        <h1>Pramuka Jabar Superapp</h1>
        <p>Frontend akan berjalan di http://localhost:3004</p>
        <p>Backend API tersedia di http://localhost:8000/api</p>
        <p>Silakan install Node.js untuk menjalankan frontend yang lengkap</p>
    </div>
</body>
</html>
EOF
fi

# Menjalankan frontend di port 3004 (APP4_PORT)
if [ -f "frontend.pid" ] && kill -0 "$(cat frontend.pid)" 2>/dev/null; then
    echo "Frontend sudah berjalan (PID: $(cat frontend.pid))."
else
    if command -v serve &> /dev/null; then
        echo "Menjalankan frontend di http://localhost:3004"
        serve -s dist -l 3004 > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo "Frontend PID: $FRONTEND_PID"
        echo $FRONTEND_PID > frontend.pid
        sleep 2
    else
        echo "serve tidak ditemukan. Frontend tidak dijalankan."
        FRONTEND_PID=""
    fi
fi

cd ..

echo ""
echo "=== Deploy selesai ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3004 (APP4_PORT)"
echo ""
if [ ! -z "$FRONTEND_PID" ]; then
    echo "Untuk berhenti: kill $BACKEND_PID $FRONTEND_PID"
else
    echo "Untuk berhenti: kill $BACKEND_PID"
fi

echo ""
if [ -f "backend.log" ]; then
    echo "--- Backend log ---"
    head -20 backend.log
fi
echo ""
if [ -f "frontend.log" ]; then
    echo "--- Frontend log ---"
    head -20 frontend.log
fi
