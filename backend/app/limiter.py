"""
Modul rate limiting terpusat menggunakan SlowAPI.

Filosofi limit per kategori endpoint:
┌─────────────────────────────┬───────────┬──────────────────────────────────────────────────────┐
│ Kategori                    │ Limit     │ Alasan                                               │
├─────────────────────────────┼───────────┼──────────────────────────────────────────────────────┤
│ Auth — login / register     │ 10/menit  │ Cegah brute-force & credential stuffing              │
│ Auth — refresh / me         │ 30/menit  │ Normal polling token refresh oleh frontend           │
│ Read (GET list)             │ 60/menit  │ Endpoint ringan tapi bisa di-spam untuk scraping     │
│ Read (GET by ID)            │ 120/menit │ Lebih spesifik, traffic normal lebih tinggi          │
│ Write (POST/PUT data)       │ 30/menit  │ Operasi DB write, tidak perlu lebih dari ini         │
│ Delete                      │ 20/menit  │ Destruktif — lebih konservatif                       │
│ Upload file                 │ 10/menit  │ Berat I/O, cegah storage abuse                      │
│ Approval (admin action)     │ 30/menit  │ Admin workflow — cukup untuk operasional normal      │
│ Dashboard (aggregasi berat) │ 30/menit  │ Query agregasi, cukup untuk polling dashboard        │
│ Admin CRUD user             │ 20/menit  │ Operasi admin, tidak perlu sangat tinggi             │
└─────────────────────────────┴───────────┴──────────────────────────────────────────────────────┘
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Gunakan IP client sebagai key identifier.
# Untuk production di belakang proxy/load balancer, pastikan
# X-Forwarded-For / X-Real-IP di-forward dengan benar oleh Nginx/Caddy.
limiter = Limiter(key_func=get_remote_address)

# ─── String limit per kategori ────────────────────────────────────────────────

# Auth
LIMIT_AUTH_STRICT   = "10/minute"   # login, register
LIMIT_AUTH_NORMAL   = "30/minute"   # refresh, me, logout

# Read
LIMIT_READ_LIST     = "60/minute"   # GET list (paginasi)
LIMIT_READ_DETAIL   = "120/minute"  # GET by ID

# Write
LIMIT_WRITE         = "30/minute"   # POST/PUT data
LIMIT_DELETE        = "20/minute"   # DELETE

# Khusus
LIMIT_UPLOAD        = "10/minute"   # upload file
LIMIT_APPROVAL      = "30/minute"   # POST approval (admin)
LIMIT_DASHBOARD     = "30/minute"   # GET dashboard (agregasi)
LIMIT_ADMIN_WRITE   = "20/minute"   # POST/PUT/DELETE admin/users
LIMIT_ADMIN_READ    = "60/minute"   # GET admin/users
