#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# migrate_and_commit.sh
# Jalankan dari root project di Git Bash:
#   bash migrate_and_commit.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

echo ""
echo "=== [1/3] Menjalankan migrasi manual ==="
cd "$BACKEND_DIR"
python migrate_manual.py

echo ""
echo "=== [2/3] Staging semua perubahan ==="
cd "$ROOT_DIR"
git add \
  backend/app/routers/auth.py \
  backend/app/routers/admin.py \
  backend/app/routers/organisasi.py \
  backend/app/routers/program.py \
  backend/app/routers/kegiatan.py \
  backend/app/routers/radit.py \
  backend/app/models.py \
  backend/app/config.py \
  backend/app/main.py \
  backend/app/database.py \
  backend/app/deps.py \
  backend/app/schemas.py \
  backend/app/utils/password.py \
  backend/app/utils/security.py \
  backend/app/auth.py \
  backend/requirements.txt \
  backend/.env.example \
  backend/migrate_manual.py \
  backend/migrations/versions/003_kegiatan_indexes.py \
  backend/migrations/versions/004_realisasi_laporan_approval_indexes.py \
  backend/migrations/versions/005_organisasi_indexes.py \
  backend/migrations/versions/006_users_indexes.py \
  backend/migrations/versions/007_programs_indexes.py \
  frontend/src/store/ereporting.js \
  frontend/src/pages/EReporting/RealisasiPage.vue \
  frontend/src/pages/EReporting/LaporanPage.vue \
  frontend/src/pages/EReporting/ApprovalPage.vue \
  frontend/src/components/Sidebar.vue \
  frontend/src/router/index.js \
  .gitattributes

echo ""
echo "=== [3/3] Commit ==="
git commit -m "feat: optimasi auth+kegiatan+realisasi API, CORS fix, modul E-Reporting

Performance:
- auth: bcrypt rounds 10, migrasi python-jose ke PyJWT, eager load role
- kegiatan: hapus COUNT redundan, joinedload program, EXISTS check, index baru
- realisasi: selectinload documents (fix N+1), EXISTS validasi FK,
  dashboard/grafik grouping di DB, statistik single query agregasi,
  approval flush tanpa refresh, index baru semua tabel

Security:
- CORS: ganti allow_origins=[*] ke eksplisit via CORS_ORIGINS env variable
- allow_credentials=True sekarang aman (tidak dikombinasikan dengan *)

Bug fix:
- create_refresh_token sebelumnya memanggil create_access_token_impl

Database:
- Tambah index: kegiatans, realisasi, dokumen, laporans, approvals
- Script migrasi manual: backend/migrate_manual.py

Frontend (Modul 3 E-Reporting):
- store/ereporting.js: Pinia store realisasi/laporan/approval/dashboard
- pages/EReporting/RealisasiPage.vue: list + create + upload dokumen
- pages/EReporting/LaporanPage.vue: list + create + stat cards
- pages/EReporting/ApprovalPage.vue: review + approve/reject laporan
- Sidebar: navigasi dikelompokkan (Dashboard, E-Reporting, Admin)
- Router: route /e-reporting/realisasi|laporan|approval"

echo ""
echo "=== DONE ==="
echo "Semua perubahan sudah di-commit. Jalankan: git push"
