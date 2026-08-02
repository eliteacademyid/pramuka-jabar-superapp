## 2. Gambaran Umum Sistem

### 2.1 Deskripsi Singkat
JavaScout adalah **superapps** berbasis web (dan target mobile app) yang menjadikan e-commerce sebagai modul inti:

- **Setiap anggota Pramuka dapat membuka toko** (store) dalam hitungan menit: daftar produk, kelola stok, dan terima pesanan.
- **UMKM lokal** dapat onboarding menjadi penjual dengan pendampingan komunitas.
- **Pembeli** dapat datang dari anggota lain maupun masyarakat umum: menjelajah katalog, berbelanja lintas toko, membayar via wallet/payment gateway, dan melacak pengiriman.
- **Superapp** berarti sistem dirancang modular: modul e-commerce menjadi fondasi, modul lain (komunitas, edukasi, event, koperasi) dapat ditambahkan tanpa merombak inti.

### 2.2 Karakteristik Pengguna (Actor)
| Actor | Peran |
|---|---|
| Tamu (Masyarakat Umum) | Melihat katalog & detail produk; wajib registrasi untuk belanja |
| Pembeli (Buyer) | Belanja: keranjang, checkout, pembayaran, lacak pesanan, ulasan |
| Penjual Anggota/UMKM (Seller) | Membuka toko, kelola produk/stok/pesanan/pengiriman, pencairan dana |
| Admin Platform | Moderasi toko & produk, kelola kategori/komisi/laporan |
| Staff (Operator Back-office) | Sama seperti Admin untuk area marketplace & user (role `staff` diterima semua API admin) |
| Super Admin | Pengaturan global: sistem, integrasi, payment, dukungan |
| Kwartir (Institusi) | Menyaksikan laporan ekonomi, promosi program UMKM Pramuka (read-only dashboard) |

### 2.3 Arsitektur Sistem
```
┌─────────────────────────────────────────────────────┐
│       Pengguna (Browser / Mobile App / PWA)          │
└─────────────────────────┬───────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────┐
│        API Gateway / Load Balancer (Nginx)          │
├─────────────────────────────────────────────────────┤
│          JavaScout SuperApp Platform (API)          │
│   ┌──────────────┬──────────────┬────────────────┐  │
│   │ Modul Auth   │ Modul E-     │ Modul Wallet   │  │
│   │ & Akun (SSO) │ commerce     │ & Pembayaran   │  │
│   ├──────────────┼──────────────┼────────────────┤  │
│   │ Modul Toko   │ Modul Order  │ Modul Komunitas│  │
│   │ & Produk     │ & Kirim      │ (rating/chat)  │  │
│   └──────────────┴──────────────┴────────────────┘  │
├─────────────────────────────────────────────────────┤
│  Database (Relational — PostgreSQL/MySQL)           │
│  + Cache (Redis) + File Storage (produk/gambar)     │
└─────────────────────────────────────────────────────┘
   Integrasi Eksternal:
   Payment Gateway (VA/QRIS/e-wallet) · Ekspedisi (ongkir)
   WhatsApp · Maps · Notifikasi (push/email)
```

Pendekatan arsitektur: **API-first modular monolith** (monolitik modular dengan batas modul jelas) agar cepat dikembangkan, dengan jalur evolusi ke microservices bila modul komunitas/payment tumbuh besar. Front-end PWA (web) sebagai kanal utama superapps.

### 2.4 Teknologi Terimplementasi (Iterasi 1)

| Lapisan | Teknologi | Keterangan |
|---|---|---|
| Backend | Python 3 + FastAPI 0.128 + SQLAlchemy 2.0 | REST/JSON, modular router per modul (`app/routers/`), service layer (`app/services/`) |
| Auth | JWT (python-jose) + bcrypt | `access_token` 120 menit; RBAC: admin / staff / anggota / umum |
| Database | PostgreSQL 16 (docker) | 16 tabel inti; transaksi atomic untuk escrow & wallet |
| Frontend | Vue 3 (Composition API) + Vite + vue-router + axios | SPA; baseURL API dinamis (`VITE_API_URL` atau host halaman:8000) agar dapat diakses via LAN |
| Deployment | Docker Compose (db, backend:8000, frontend:5173) | Seed otomatis akun admin & demo data saat startup |
| Testing | pytest + httpx (TestClient, SQLite) | 95 test: auth (termasuk tema per-user), toko/produk, keranjang, order, wallet, ulasan, chat, admin (termasuk RBAC staff, monitor keranjang user, lokasi & sort harga, saran pencarian, sort rating & banyak ulasan, chat mandiri pra-pesanan & unread, notifikasi in-app, tiket perselisihan) |

---

