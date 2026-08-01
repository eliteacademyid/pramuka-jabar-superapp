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
git commit -m "security: hardening auth, validation, rate-limit, role-check, file-upload

Security:
- schemas.py: semua field punya max_length, Enum untuk status/role (RealisasiStatusEnum,
  LaporanStatusEnum, ApprovalStatusEnum, RoleEnum) — tidak bisa inject nilai arbitrary,
  username validator alphanumeric, password max 128
- radit.py: POST /approval sekarang admin-only via get_current_admin
- radit.py: dashboard/* sekarang require autentikasi (get_current_user)
- radit.py: upload validasi ekstensi whitelist + max 10MB + sanitasi nama file
  (cegah path traversal) + error Cloudinary tidak bocor ke client
- program.py & kegiatan.py: ganti hardcoded role_id==1 dengan role.name=='admin'
  via helper _is_admin() — tidak pecah jika role ID bergeser
- kegiatan.py: guard null program pada permission check (cegah AttributeError)
- main.py: rate limiter 10 req/menit per IP pada /login dan /register
- main.py: security headers (X-Content-Type-Options, X-Frame-Options, HSTS di production)
- main.py: docs/redoc/openapi disembunyikan di ENVIRONMENT=production
- config.py: validasi SECRET_KEY kuat saat production + token expire turun 120→60 menit
- .env: SECRET_KEY diperbarui ke 64-char hex

Performance (tidak ada perubahan):
- Semua bottleneck DB dari sesi sebelumnya sudah bersih"

echo ""
echo "=== DONE ==="
echo "Semua perubahan sudah di-commit. Jalankan: git push"
