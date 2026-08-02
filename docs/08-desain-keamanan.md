## 8. Desain Keamanan

- **Transport**: HTTPS seluruh domain/CDN.
- **Autentikasi**: password di-hash (bcrypt/argon2); OTP WhatsApp opsional; token refresh + akses (JWT) dengan masa berlaku; proteksi brute-force & rate limiting.
- **Otorisasi**: RBAC (tamu, pembeli, penjual, admin, superadmin); penjual hanya akses tokonya (scope store_id); middleware per modul.
- **Input handling**: validasi & sanitasi (XSS), prepared statements/ORM (SQLi), batas ukuran & MIME upload gambar produk, validasi alamat & harga.
- **Transaksi**: idempotency key pada pembayaran; transaksi DB atomic (order → payment → escrow); escrow konsisten dengan audit trail; log mutasi wallet.
- **Kepatuhan pembayaran**: integrasi gateway via server-to-server, tanpa menyimpan data kartu (PCI-DSS di-handle gateway); penandatanganan callback/notifikasi.
- **Data pribadi**: enkripsi data sensitif; prinsip minimal data; kepatuhan UU PDP; hapus akun.
- **CSRF token** pada semua form; header keamanan (CSP, HSTS).
- **Backup**: database & media terjadwal; uji restore.

---

