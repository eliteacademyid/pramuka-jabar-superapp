## 9. Deployment & Infrastruktur

| Komponen | Keterangan |
|---|---|
| Platform | SuperApp web (PWA) — target Android/iOS selanjutnya |
| Domain | javascout.id (utama), cdn.javascout.id (aset/gambar produk) |
| Backend | FastAPI (Python) + SQLAlchemy — REST/JSON, modular router + service layer |
| Frontend | Vue 3 + Vite + axios (SPA) — katalog publik SEO-friendly (SSR/ISR opsional) |
| Database | PostgreSQL 16 + SQLite (untuk test otomatis) |
| Kontainerisasi | Docker Compose (podman-compatible): `db` (5432), `backend` (8000), `frontend` (5173) — healthcheck DB, seed otomatis saat startup |
| Akses lokal/LAN | Frontend otomatis menunjuk API pada host yang sama (port 8000) atau via `VITE_API_URL`; backend & frontend listen `0.0.0.0` |
| Storage | Object storage (S3-compatible) + CDN (rencana) |
| Payment | Wallet internal (top-up mock) — payment gateway QRIS/VA/e-wallet (rencana) |
| Ekspedisi | Ongkir tier statis (Tier A/B/C) — integrasi API ongkir (rencana) |
| Monitoring | Logging terpusat, APM, alert uptime (rencana) |
| Backup | Harian DB + media; snapshot mingguan (rencana) |

