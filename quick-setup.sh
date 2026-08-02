#!/bin/bash

# Quick setup for Pramuka Jabar Superapp
# Run backend on port 8000 and frontend on port 3003

cd /home/opencode/team4/pramuka-jabar-superapp

echo "=== Starting Pramuka Jabar Superapp ==="

echo "Checking dependencies..."

# Setup backend
echo "Setting up backend..."
cd backend

# Buat virtual environment jika belum ada
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Export environment variables - gunakan SQLite sebagai fallback jika PostgreSQL tidak tersedia
if pg_isready -q; then
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

echo "Running backend on http://localhost:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
echo $BACKEND_PID > backend.pid

cd ..

# Setup frontend
echo "Setting up frontend..."
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Build frontend
echo "Building frontend..."
npm run build

# Install serve
if ! command -v serve &> /dev/null; then
    echo "Installing serve..."
    npm install -g serve
fi

echo "Running frontend on http://localhost:3003"
serve -s dist -l 3003 > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"
echo $FRONTEND_PID > frontend.pid

cd ..

echo ""
echo "=== Setup selesai ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3003"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"

# Tampilkan log jika backend/frontend gagal memulai
cat backend.log 2>/dev/null | head -20
echo "Check frontend.log for frontend output"
