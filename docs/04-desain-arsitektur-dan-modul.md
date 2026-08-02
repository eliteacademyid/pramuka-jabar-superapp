## 4. Desain Arsitektur & Modul

### 4.1 Diagram Modul
```
JavaScout SuperApp
├── Modul Akun & SSO
│   ├── Registrasi (anggota & umum)
│   ├── Verifikasi keanggotaan Pramuka
│   └── Profil & alamat
├── Modul Toko
│   ├── Onboarding & verifikasi toko
│   └── Halaman publik toko (/store/{slug})
├── Modul Produk & Katalog
│   ├── CRUD produk + varian + foto
│   ├── Kategori & pencarian
│   └── Promosi/banner
├── Modul Keranjang & Checkout
│   ├── Multi-store cart
│   └── Ongkir & diskon
├── Modul Order & Pengiriman
│   ├── Siklus status pesanan
│   └── Integrasi ekspedisi
├── Modul Pembayaran & Wallet
│   ├── Wallet + escrow
│   ├── Payment gateway
│   └── Pencairan dana
├── Modul Ulasan & Chat
├── Modul Notifikasi
├── Modul Back-office Admin
└── Modul Laporan & Dashboard
```

### 4.2 Alur Utama

**A. Alur Anggota Membuka Toko**
1. Anggota login (SSO) → menu "Buka Toko".
2. Isi formulir onboarding (data toko + identitas) → submit.
3. Sistem simpan draft toko → kirim notifikasi admin.
4. Admin verifikasi & setujui → toko aktif, URL `/store/{slug}` siap.
5. Penjual mulai menambahkan produk.

**B. Alur Pembelian (Pembeli Umum)**
1. Pembeli (anggota/umum) mencari produk → tambah ke keranjang.
2. Checkout: pilih alamat, ekspedisi, metode bayar → sistem buat order + tagihan.
3. Pembeli bayar (wallet/gateway) → dana masuk escrow.
4. Penjual proses & kirim (input resi) → pembeli terima & konfirmasi.
5. Sistem lepas escrow ke penjual (dikurangi komisi) → pembeli beri ulasan
   (klik **bintang 1–5** + komentar pada halaman detail pesanan; rating tampil
   di detail produk & kartu katalog).

**C. Alur Pencairan Dana Penjual**
1. Penjual buka dashboard → saldo tersedia.
2. Ajukan withdraw → sistem verifikasi saldo & rekening tujuan.
3. Diproses admin/finance → dana terkirim → riwayat tercatat.

**D. Alur Moderasi Produk**
1. Penjual submit produk baru/ubah.
2. Sistem filter otomatis (kata terlarang, gambar) → antrean moderasi.
3. Admin tinjau & setujui/tolak → status produk diperbarui, notifikasi penjual.

### 4.3 Pola Desain
- **Modular monolith / modul berbatas** — setiap modul punya entitas, service, dan controller-nya sendiri.
- **Repository/Service layer** untuk logika bisnis; controller tipis.
- **DTO/Resource** untuk respons API; validasi terpusat (request rules).
- **Event-driven internal** (mis. `OrderPaid`, `OrderShipped`) untuk notifikasi & escrow.
- **Idempotency key** pada endpoint pembayaran untuk mencegah duplikasi.
- Front-end: PWA SPA (React/Vue) + API REST/JSON; atau server-rendered untuk SEO halaman publik katalog.

---

