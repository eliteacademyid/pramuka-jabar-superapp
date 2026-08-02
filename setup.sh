#!/bin/bash

# Pramuka Jabar Superapp - Setup & Run Script
# Jalankan backend di port 8000 dan frontend di port 3003

set -e

PROJECT_DIR="/home/opencode/team4/pramuka-jabar-superapp"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cek PostgreSQL
check_postgres() {
    log_info "Memeriksa PostgreSQL..."
    if ! command -v psql &> /dev/null; then
        log_warn "psql tidak ditemukan. Menginstal PostgreSQL client..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y postgresql-client 2>/dev/null || log_warn "Gagal menginstal postgresql-client, melanjutkan..."
        elif command -v yum &> /dev/null; then
            sudo yum install -y postgresql-client
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y postgresql-client
        else
            log_warn "Tidak bisa menginstal PostgreSQL client. Memeriksa server PostgreSQL lokal..."
        fi
    fi

    if ! pg_isready -q; then
        log_warn "PostgreSQL tidak berjalan di localhost:5432."
        log_info "Mencoba membuat database lokal menggunakan sqlite3 sebagai fallback..."
        return 1
    fi

    # Cek koneksi ke database
    if sudo -u postgres psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw db_pramuka_jabar; then
        log_info "Database db_pramuka_jabar sudah ada."
    else
        # Coba buat database
        if id postgres &>/dev/null; then
            log_info "Membuat database db_pramuka_jabar..."
            sudo -u postgres psql -c "CREATE DATABASE db_pramuka_jabar;" 2>/dev/null && log_info "Database db_pramuka_jabar dibuat." || log_warn "Gagal membuat database, melanjutkan..."
        else
            log_warn "User postgres tidak ditemukan. Mencoba menggunakan user default..."
            # Coba sebagai current user
            psql -lqt 2>/dev/null | grep -qw db_pramuka_jabar || \
                psql -c "CREATE DATABASE db_pramuka_jabar;" 2>/dev/null && echo "Database dibuat secara lokal" || log_warn "Gagal membuat database secara lokal, melanjutkan..."
        fi
    fi
}

# Setup backend
setup_backend() {
    log_info "=== Setup Backend ==="
    cd "$BACKEND_DIR"

    # Buat virtual environment
    if [ ! -d "venv" ]; then
        log_info "Membuat virtual environment..."
        python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    # Install requirements
    if [ -f "requirements.txt" ]; then
        log_info "Menginstal dependencies backend..."
        pip install -r requirements.txt
    fi

    # Setup .env
    if [ ! -f ".env" ]; then
        log_info "Membuat file .env..."
        cp .env.example .env
        log_warn "Silakan edit file .env dan sesuaikan nilai sesuai kebutuhan."
        log_warn "DATABASE_URL mungkin perlu diubah tergantung environment."
    fi

    # Cek database - jika PostgreSQL tidak tersedia, gunakan SQLite
    if pg_isready -q; then
        log_info "PostgreSQL tersedia, menggunakan database PostgreSQL."
        export DATABASE_URL="${DATABASE_URL:-postgresql://postgres@localhost:5432/db_pramuka_jabar}"
    else
        log_warn "PostgreSQL tidak tersedia, menggunakan SQLite sebagai fallback."
        log_warn "Buat database SQLite di project directory: api.db"
        export DATABASE_URL="sqlite:///api.db"
    fi

    export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
    export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-120}"

    # Simpan PID backend
    BACKEND_PID_FILE="backend.pid"
    if [ -f "$BACKEND_PID_FILE" ] && kill -0 "$(cat $BACKEND_PID_FILE)" 2>/dev/null; then
        log_info "Backend sudah berjalan (PID: $(cat $BACKEND_PID_FILE))."
    else
        log_info "Menjalankan backend di http://localhost:8000..."
        log_info "Database: $DATABASE_URL"
        uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
        echo $! > "$BACKEND_PID_FILE"
        log_info "Backend PID: $!"
    fi

    cd - > /dev/null
}

# Setup frontend
setup_frontend() {
    log_info "=== Setup Frontend ==="
    cd "$FRONTEND_DIR"

    # Install dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Menginstal dependencies frontend..."
        npm install
    fi

    # Build frontend
    log_info "Mem-build frontend..."
    npm run build

    # Cek port 3003
    FRONTEND_PID_FILE="frontend.pid"
    if [ -f "$FRONTEND_PID_FILE" ] && kill -0 "$(cat $FRONTEND_PID_FILE)" 2>/dev/null; then
        log_info "Frontend sudah berjalan (PID: $(cat $FRONTEND_PID_FILE))."
    else
        # Install serve jika belum ada
        if ! command -v serve &> /dev/null; then
            log_info "Menginstal serve..."
            npm install -g serve
        fi

        log_info "Menjalankan frontend di http://localhost:3003..."
        serve -s dist -l 3003 > frontend.log 2>&1 &
        echo $! > "$FRONTEND_PID_FILE"
        log_info "Frontend PID: $!"
    fi

    cd - > /dev/null
}

# Setup API service configuration
setup_api_service() {
    log_info "=== Setup API Service ==="
    
    # Create simple systemd-like service script for local development
    SERVICE_SCRIPT="$PROJECT_DIR/run-services.sh"
    cat > "$SERVICE_SCRIPT" << 'EOF'
#!/bin/bash

PROJECT_DIR="/home/opencode/team4/pramuka-jabar-superapp"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
    echo -e "${YELLOW}[INFO]${NC} Membersihkan process..."
    if [ -f "$PROJECT_DIR/backend/backend.pid" ]; then
        kill $(cat "$PROJECT_DIR/backend/backend.pid") 2>/dev/null || true
        rm -f "$PROJECT_DIR/backend/backend.pid"
    fi
    if [ -f "$PROJECT_DIR/frontend/frontend.pid" ]; then
        kill $(cat "$PROJECT_DIR/frontend/frontend.pid") 2>/dev/null || true
        rm -f "$PROJECT_DIR/frontend/frontend.pid"
    fi
}

# Cleanup saat exit
trap cleanup EXIT

# Setup database
check_postgres() {
    echo -e "${YELLOW}[INFO]${NC} Memeriksa PostgreSQL..."
    if ! pg_isready -q; then
        echo -e "${YELLOW}[WARN]${NC} PostgreSQL tidak berjalan. Silakan jalankan PostgreSQL dan coba lagi."
        return 1
    fi

    if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw db_pramuka_jabar; then
        echo -e "${YELLOW}[INFO]${NC} Membuat database db_pramuka_jabar..."
        sudo -u postgres psql -c "CREATE DATABASE db_pramuka_jabar;"
    fi
}

# Setup backend
setup_backend() {
    echo -e "${GREEN}[INFO]${NC} Setup backend..."
    cd "$BACKEND_DIR"
    source venv/bin/activate

    # Setup environment - gunakan SQLite jika PostgreSQL tidak tersedia
    if pg_isready -q; then
        export DATABASE_URL="${DATABASE_URL:-postgresql://postgres@localhost:5432/db_pramuka_jabar}"
        echo -e "${GREEN}[INFO]${NC} Database: PostgreSQL"
    else
        export DATABASE_URL="sqlite:///api.db"
        echo -e "${YELLOW}[WARN]${NC} Database: SQLite (fallback)"
    fi

    export SECRET_KEY="${SECRET_KEY:-$(openssl rand -hex 32)}"
    export ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-120}"

    # Buat .env jika belum ada
    if [ ! -f .env ]; then
        cp .env.example .env
    fi

    # Jalankan backend
    echo -e "${GREEN}[INFO]${NC} Menjalankan backend di http://localhost:8000..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000
}

# Setup frontend
setup_frontend() {
    echo -e "${GREEN}[INFO]${NC} Setup frontend..."
    cd "$FRONTEND_DIR"
    npm run build
    serve -s dist -l 3003
}

# Main
main() {
    # Cek dan setup database
    check_postgres || return 1

    # Setup backend
    setup_backend &
    BACKEND_PID=$!

    # Tunggu backend siap
    echo -e "${YELLOW}[INFO]${NC} Menunggu backend siap..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null || curl -s http://localhost:8000/ > /dev/null; then
            echo -e "${GREEN}[INFO]${NC} Backend siap!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "${RED}[ERROR]${NC} Backend tidak siap setelah 30 detik"
            return 1
        fi
    done

    # Setup frontend
    setup_frontend
}

main
EOF

    chmod +x "$SERVICE_SCRIPT"
    log_info "Script service dibuat: $SERVICE_SCRIPT"
}

# Main
main() {
    log_info "=== Pramuka Jabar Superapp Setup ==="

    # Cek project directory
    if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
        log_error "Struktur project tidak valid. Pastikan berada di directory yang benar."
        exit 1
    fi

    # Cek/Setup PostgreSQL
    check_postgres

    # Setup backend
    setup_backend

    # Setup frontend
    setup_frontend

    # Setup API service
    setup_api_service

    log_info "=== Setup Selesai ==="
    log_info "Backend: http://localhost:8000"
    log_info "Frontend: http://localhost:3003"
    log_info ""
    log_info "Untuk berhenti: kill $(cat backend.pid) $(cat frontend.pid)"
    log_info "Atau jalankan: $PROJECT_DIR/run-services.sh"
}

# Jalankan main
main
