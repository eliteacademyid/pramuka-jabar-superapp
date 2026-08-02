## 1. Pendahuluan

### 1.1 Tujuan
Dokumen ini merupakan Spesifikasi Desain Perangkat Lunak (SDD) untuk **JavaScout**, platform superapps yang menjadi pusat pemberdayaan ekonomi anggota Gerakan Pramuka dan UMKM lokal. Dokumen ini mendeskripsikan desain arsitektur, modul, alur data, kebutuhan fungsional dan non-fungsional sebagai acuan pengembangan, pemeliharaan, dan pengembangan lanjutan sistem.

### 1.2 Objektif
Platform e-commerce untuk pemberdayaan ekonomi anggota Pramuka dan UMKM lokal. Anggota dapat membuka toko, memasarkan produk, dan melayani pembelian dari anggota lain maupun masyarakat umum.

### 1.3 Ruang Lingkup
Sistem mencakup:
1. **Superapp platform** dengan arsitektur modular (satu aplikasi, banyak modul/kanal layanan).
2. **Modul E-commerce (marketplace)** — inti sistem: toko anggota/UMKM, katalog produk, keranjang, checkout, pembayaran, pengiriman, ulasan.
3. **Modul Akun Anggota (SSO)** — profil, verifikasi keanggotaan Pramuka (KWK/KWARDA/KWARCAB/KWARRAN), dompet digital (wallet).
4. **Modul Komunitas** — direktori toko, rating, umpan balik, promosi (banner/kanal khusus).
5. **Back-office Admin** — manajemen toko, moderasi produk, laporan, pengaturan komisi.
6. **Integrasi eksternal** — payment gateway, jasa ekspedisi (ongkir), WhatsApp, peta lokasi toko.

### 1.4 Definisi & Istilah
| Istilah | Definisi |
|---|---|
| SuperApp | Aplikasi terpadu yang menghimpun banyak layanan dalam satu platform (modul) |
| Anggota Pramuka | Anggota Gerakan Pramuka terdaftar & terverifikasi (Siaga–Pembina, Kwartir, DKR/DKC, dsb.) |
| UMKM Lokal | Usaha mikro, kecil, menengah di lingkungan komunitas Pramuka / daerah setempat |
| Toko (Store) | Kanal penjualan milik anggota/UMKM di dalam platform |
| Marketplace | Area publik untuk menemukan & membeli produk dari berbagai toko |
| Wallet | Dompet digital internal untuk saldo, transaksi, dan pencairan penjual |
| KWK | Kartu Wajib Koperasi? / Kartu keanggotaan — verifikasi identitas Pramuka |
| SSO | Single Sign-On — satu akun untuk semua modul |
| Onboarding | Proses pendaftaran & aktivasi toko baru |

### 1.5 Referensi
- Anggaran Dasar/Anggaran Rumah Tangga Gerakan Pramuka
- Peraturan Kwartir Nasional tentang Koperasi & Usaha Kwartir
- Pedoman layanan e-commerce (gambar produk, ongkir, retur)
- Panduan keamanan aplikasi OWASP Top 10 & PCI-DSS (penanganan pembayaran)

---

