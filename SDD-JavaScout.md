# SDD (Software Design Document) — JavaScout SuperApp

**Nama Sistem** : JavaScout — SuperApp Pemberdayaan Ekonomi Pramuka & UMKM Lokal
**Versi Dokumen** : 1.11
**Tanggal** : 2 Agustus 2026
**Status** : Draft — Iterasi 1 (modul marketplace inti telah diimplementasikan)

> **Catatan Implementasi Iterasi 1 (tim 1)**: Modul e-commerce/marketplace telah
> diimplementasikan dan diuji (74 test lulus): registrasi & login (JWT), toko,
> katalog produk, keranjang lintas toko, checkout + ongkir, pembayaran via wallet
> dengan escrow & komisi platform, siklus pesanan (pay → confirm → ship →
> confirm-receipt), pencairan dana penjual (withdraw + moderasi admin), ulasan,
> chat pembeli–penjual, serta back-office admin (moderasi toko/produk, laporan).
> Pembaruan v1.2: penghapusan user tidak lagi gagal (500) — user yang masih punya
> data transaksi otomatis dinonaktifkan (soft delete); katalog ditambah kartu
> kategori (klik untuk memfilter), badge keranjang, dan toast konfirmasi tambah.
> Pembaruan v1.3: landing page didesain ulang (hero foto Pramuka Jabar, strip
> statistik, kartu fitur, kategori populer, band CTA, topbar/footer baru); semua
> gambar produk kini foto nyata yang disimpan lokal (bukan URL CDN mati) dengan
> seed diperbarui; ejaan "SuperApps" (satu kata) digunakan di UI publik.
> Pembaruan v1.4: **login & menu berbasis role** — role `staff` kini berlaku
> sebagai operator back-office (boleh akses seluruh API & menu admin, sebelumnya
> hanya `admin`); setelah login setiap user diarahkan sesuai peran (admin/staff →
> Dashboard Admin, member bertoko → Dashboard Penjual, member biasa → Katalog);
> menu "Toko Saya" hanya tampil bagi pemilik toko aktif, dan rute penjual
> (`/account/seller/*`) dilindungi (tanpa toko aktif dialihkan ke Keranjang);
> halaman login berubah dari "Masuk Admin" menjadi "Masuk" untuk semua user.
> Back-office mendapat halaman baru **Keranjang Belanja** (`GET /api/admin/carts`)
> untuk memantau isi keranjang setiap user (jumlah item, qty, subtotal, waktu
> terakhir diubah).
> Pembaruan v1.5: **pencarian produk di landing page** — kolom pencarian pill di
> hero beranda; menekan Cari/Enter mengarahkan ke `/catalog?q=…` dengan kata
> kunci otomatis terisi pada kolom pencarian katalog dan hasil langsung terfilter
> (FR-12, backend `GET /api/products?q=…` mencocokkan nama & deskripsi).
> Pembaruan v1.6: **pencarian berdasarkan lokasi & sort harga** — kolom pencarian
> landing kini dua bagian (produk + kota) mengarah ke `/catalog?q=…&city=…`;
> filter lokasi di katalog memakai partial-match (`%city%`) dengan saran kota
> dari `GET /api/cities` (datalist); sort harga termurah/termahal
> (`?sort=cheapest|expensive`) di katalog; respons produk menyertakan kota toko
> (`store.city`).
> Pembaruan v1.7: **rating barang dengan bintang** — form ulasan di halaman
> detail pesanan kini memakai komponen bintang interaktif `StarRating` (klik
> bintang 1–5, sebelumnya dropdown); halaman detail produk menampilkan bintang
> per ulasan dan ringkasan rata-rata bintang; kartu produk menampilkan rating
> bintang emas.
> Pembaruan v1.8: **saran pencarian otomatis** — saat mengetik di kolom
> pencarian landing page maupun katalog, muncul dropdown saran produk serupa
> (komponen `SearchSuggest.vue` dengan debounce 250 ms) dari endpoint baru
> `GET /api/products/suggest?q=…&limit=6` (cocok nama, urut produk terlaris);
> pilih saran langsung menuju halaman detail produk.
> Pembaruan v1.9: **urutkan katalog berdasarkan ulasan pembeli** — opsi
> "Rating Tertinggi" (`?sort=rating`, rata-rata bintang ulasan terbaik,
> produk tanpa ulasan di belakang) dan "Terbanyak Diulas" (`?sort=reviewed`,
> jumlah ulasan terbanyak) di dropdown urutkan katalog.
> Pembaruan v1.10: **produk jasa dummy & gambar ilustrasi** — kategori Jasa
> kini terisi 3 contoh layanan (fotografi kegiatan, desain logo & umbul-umbul,
> sewa tenda & perlengkapan) lengkap dengan gambar ilustrasi lokal
> (`frontend/public/images/products/jasa-*.jpg`); kartu kategori "Semua
> Barang" di katalog; pencarian & filter dipindah ke panel samping katalog.
> Pembaruan v1.11: **larangan konten negatif** — form produk penjual
> menampilkan peringatan larangan mengunggah gambar/konten negatif (tidak
> senonoh, pornografi, ketelanjangan, SARA, melanggar hukum) dengan sanksi
> penghapusan gambar & penonaktifan akun; backend memvalidasi URL gambar
> produk hanya http(s) atau path lokal `/images/` (skema lain seperti
> `javascript:`/`ftp:` ditolak 422); gambar ilustrasi produk jasa diperbarui
> agar sesuai kaidah kesopanan.
> Pembaruan v1.12: **halaman chat mandiri** — percakapan kini tidak lagi
> hanya terikat pesanan: pembeli dapat memulai chat ke penjual langsung dari
> halaman produk (tombol "Chat Penjual", `POST /api/conversations` membuat
> percakapan pra-pesanan per produk; dibatalkan bila berchat dengan toko
> sendiri); halaman `/account/chat` (dua panel: daftar percakapan + thread)
> menampilkan nama toko, produk, pratinjau pesan terakhir, jumlah pesan belum
> dibaca, dan pembaruan otomatis (polling); akses dibatasi pembeli–penjual–
> admin; 82 test otomatis.
> Pembaruan v1.13: **inbox penjual & badge pesan belum dibaca** — menu "Pesan
> Masuk" khusus penjual di sidebar Toko Saya (`/account/seller/chat`)
> menampilkan percakapan dari pembeli saja (filter `i_am_seller` per
> percakapan, nama lawan bicara tampil sebagai pembeli); menu Chat di sidebar
> akun menampilkan badge jumlah pesan belum dibaca (total & khusus penjual)
> yang diperbarui otomatis via polling; 82 test otomatis.
> Pembaruan v1.14: **pencarian katalog pindah ke atas kategori** — bar
> pencarian tidak lagi di panel samping: kini berupa pil pencarian lebar di
> tengah, tepat di bawah banner hero dan di atas kartu kategori (overlap tipis
> pada tepi bawah banner); panel samping katalog hanya berisi filter
> (kategori, lokasi, urutkan).
> Deskripsi pada dokumen ini mengikuti implementasi aktual pada bagian yang sudah
> dibangun; bagian lain (payment gateway, ekspedisi pihak ketiga, kupon, varian
> produk, notifikasi) tetap merupakan rencana pengembangan lanjutan.

---

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
| Testing | pytest + httpx (TestClient, SQLite) | 82 test: auth, toko/produk, keranjang, order, wallet, ulasan, chat, admin (termasuk RBAC staff, monitor keranjang user, lokasi & sort harga, saran pencarian, sort rating & banyak ulasan, chat mandiri pra-pesanan & unread) |

---

## 3. Kebutuhan Sistem

### 3.1 Kebutuhan Fungsional

#### FR-01 Registrasi & Verifikasi Akun (SSO)
- Registrasi dua jalur: anggota Pramuka (verifikasi keanggotaan: nomor anggota, pangkalan/Kwartir) dan masyarakat umum (email/telepon).
- Satu akun untuk semua modul (SSO); login via email/telepon + password atau WhatsApp OTP.
- Profil: nama, foto, alamat pengiriman (multi-alamat), kontak.

#### FR-02 Onboarding Toko (Open Store)
- Anggota/UMKM mengajukan pembukaan toko: nama toko, slug/URL toko, deskripsi, logo, alamat, kategori usaha, dokumen identitas.
- Alur verifikasi & persetujuan admin (aktif/nonaktif toko).
- Setiap toko memiliki halaman publik sendiri (`/store/{slug}`).

#### FR-03 Katalog & Manajemen Produk
- CRUD produk per toko: nama, deskripsi, kategori, harga, stok, varian (ukuran/warna), SKU, foto (multi-gambar), status (draft/aktif/arsip).
- Pencarian & filter katalog: kata kunci, kategori, lokasi toko, harga, rating, terlaris.
- Produk unggulan per toko dan sorotan platform (promosi).

#### FR-04 Keranjang & Checkout
- Keranjang belanja lintas toko (multi-store cart).
- Checkout: alamat pengiriman, pilih ekspedisi, kalkulasi ongkir, kupon/diskon, ringkasan biaya.
- Pilihan pembayaran: wallet JavaScout, payment gateway (VA/QRIS/e-wallet), bayar di toko (COD terbatas).

#### FR-05 Order & Pengiriman
- Status pesanan: menunggu pembayaran → dikonfirmasi → diproses → dikirim → selesai / dibatalkan / retur.
- Pencetakan label/resi, input nomor resi, lacak pengiriman.
- Konfirmasi penerimaan oleh pembeli; auto-complete setelah batas waktu.

#### FR-06 Pembayaran & Wallet
- Dompet digital: top-up, saldo, histori transaksi.
- Pembayaran pesanan dari saldo; escrow (dana penahanan) hingga pesanan selesai.
- Pencairan dana penjual (withdraw) ke rekening/e-wallet.

#### FR-07 Ulasan & Rating
- Pembeli memberi rating (1–5) + ulasan per produk & per toko setelah pesanan selesai.
- Moderasi ulasan oleh admin.
- **Implementasi v1.7**: input rating berupa bintang interaktif (klik 1–5,
  komponen `StarRating.vue` — mode input di detail pesanan, mode readonly di
  detail produk & kartu); detail produk menampilkan rata-rata bintang; rating
  otomatis diperbarui pada katalog/detail.

#### FR-08 Chat & Notifikasi
- Percakapan pembeli–penjual (chat thread), terkait pesanan maupun pra-pesanan.
- **Implementasi v1.12**: chat mandiri — tombol "Chat Penjual" di detail produk
  membuat percakapan per produk (`POST /api/conversations`, idempotent per
  pembeli–produk); halaman `/account/chat` dua panel (daftar percakapan: nama
  toko, produk/pesanan, pesan terakhir, waktu, badge belum dibaca; thread pesan
  dengan balon kiri/kanan); polling otomatis 4–5 detik untuk pesan & daftar;
  read receipt (`read_at`) ditandai saat percakapan dibuka; akses pembeli,
  pemilik toko, dan admin.
- **Implementasi v1.13**: inbox penjual — menu "Pesan Masuk" pada sidebar Toko
  Saya (`/account/seller/chat`, butuh toko aktif) menampilkan hanya percakapan
  yang user-nya berperan penjual (filter `i_am_seller` dari `GET
  /api/conversations`), dengan nama lawan bicara pembeli; sidebar akun menampilkan
  badge angka pesan belum dibaca pada menu Chat (semua percakapan) dan pada menu
  Pesan Masuk (khusus peran penjual), diperbarui polling 10 detik via
  `AccountLayout.vue`; pada katalog detail, percakapan pesanan menampilkan nama
  toko sedangkan percakapan pra-pesanan menampilkan pembeli.
- Notifikasi: status pesanan, pembayaran, pengiriman, promosi (in-app/push/email/WhatsApp).

#### FR-09 Dashboard Penjual
- Statistik toko: penjualan, pesanan, produk terlaris, saldo.
- Kelola produk, stok, pesanan, kupon, pengaturan ongkir, profil toko.

#### FR-10 Back-office Admin
- Moderasi toko & produk, kelola kategori, komisi platform per penjualan.
- Kelola pengguna, dispute/keluhan, kupon platform, banner promosi.
- Laporan: transaksi, penjualan per toko/kategori/periode (ekspor CSV).

#### FR-11 Konten & Promosi (Modul Komunitas)
- Banner/kanal promosi: produk unggulan, toko pilihan, program "UMKM Pramuka".
- Feed kegiatan ekonomi komunitas (opsional modul lanjutan).

#### FR-12 Pencarian Global
- Pencarian produk, toko, dan kategori secara terpadu dengan saran otomatis.
- **Implementasi v1.5 & v1.6**: pencarian produk dari landing page (kolom
  pencarian produk + kota di hero) → katalog dengan kata kunci/lokasi terisi
  (`GET /api/products?q=…&city=…`, cocok nama & deskripsi serta lokasi
  partial-match, tidak peka huruf besar/kecil); sort harga termurah/termahal
  (`?sort=cheapest|expensive`); kombinasi dengan filter kategori didukung;
  tanpa hasil menampilkan state kosong.
- **Implementasi v1.8**: saran otomatis saat mengetik — `SearchSuggest.vue`
  (debounce 250 ms) memanggil `GET /api/products/suggest?q=…&limit=6` dan
  menampilkan dropdown produk serupa (nama, gambar, harga, toko, jumlah
  terjual); navigasi keyboard (↑/↓/Enter/Esc) didukung; memilih saran
  langsung membuka halaman detail produk.
- **Implementasi v1.9**: urutkan berdasarkan ulasan pembeli — "Rating
  Tertinggi" (`?sort=rating`, rata-rata bintang ulasan visible menurun,
  produk tanpa ulasan berada di akhir) dan "Terbanyak Diulas"
  (`?sort=reviewed`, jumlah ulasan visible menurun) di dropdown urutkan
  katalog; keduanya dapat dikombinasikan dengan filter & pencarian lain.

### 3.2 Kebutuhan Non-Fungsional

| Kode | Aspek | Spesifikasi |
|---|---|---|
| NFR-01 | Kinerja | Muat halaman < 3 detik; API response p95 < 500 ms; caching Redis; CDN gambar produk |
| NFR-02 | Keamanan | HTTPS; hashing password; JWT/session aman; RBAC; validasi & sanitasi input (XSS/SQLi); OWASP; proteksi brute-force; kepatuhan pembayaran |
| NFR-03 | Skalabilitas | Modular — penambahan modul (koperasi, event, edukasi) tanpa rombak inti; siap naik skala vertikal/horizontal |
| NFR-04 | Kompatibilitas | Responsive web (PWA), target iOS/Android; browser modern |
| NFR-05 | SEO | Slug URL, meta tag, sitemap, structured data produk (Schema.org) |
| NFR-06 | Keandalan | Backup DB & media terjadwal; transaksi atomic; escrow konsisten; uptime tinggi |
| NFR-07 | Aksesibilitas | WCAG 2.1 AA: heading, alt text, kontras, navigasi keyboard |
| NFR-08 | Keamanan data pribadi | Kepatuhan UU PDP; enkripsi data sensitif; riwayat aktivitas |
| NFR-09 | Audit trail | Log semua transaksi, perubahan produk, moderasi |

---

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

## 5. Desain Basis Data

### 5.1 ERD (Relasi Entitas)
```
users (1)──(n) stores (1)──(n) products (1)──(n) product_variants
stores (1)──(n) orders *──────────* products (order_items)
users (1)──(n) orders (buyer)
stores (1)──(n) reviews (rating produk & toko)
users (1)──(1) wallets (1)──(n) wallet_transactions
orders (1)──(1) payments · (1)──(1) shipments
users (1)──(n) addresses · (1)──(n) conversations/messages
categories (1)──(n) products · coupons (n)──(n) orders?
```

### 5.2 Skema Tabel Utama

**users**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| name | varchar | |
| email / phone | varchar unique | login |
| password | varchar (hash) | |
| role | enum | member / seller / admin / superadmin |
| scout_number / kwk_number | varchar nullable | verifikasi anggota |
| kwartir_id | int FK nullable | pangkalan/Kwartir asal |
| is_verified | boolean | verifikasi keanggotaan |
| status | enum | active / suspended |
| created_at / updated_at | datetime | |

**stores**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| owner_id | bigint FK → users | |
| name | varchar | nama toko |
| slug | varchar unique | URL `/store/{slug}` |
| description | text | |
| logo / banner | varchar | |
| category_id | int FK | sektor usaha |
| address / lat / lng | text / decimal | lokasi toko |
| status | enum | pending / active / suspended / rejected |
| commission_rate | decimal | komisi platform |
| created_at / updated_at | datetime | |

**products**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| store_id | bigint FK | |
| category_id | int FK | |
| name | varchar | |
| slug | varchar unique | |
| description | text | |
| price | decimal(14,2) | |
| stock | int | |
| sku | varchar | |
| images | json | daftar URL gambar |
| status | enum | draft / active / archived / rejected |
| views / sold | int | popularitas |
| created_at / updated_at | datetime | |

**product_variants**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| product_id | bigint FK | |
| name / value | varchar | mis. ukuran "L", warna "Merah" |
| price / stock | decimal / int | overrides |

**orders**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_code | varchar unique | tampil ke user |
| buyer_id | bigint FK → users | |
| store_id | bigint FK | satu order per toko (multi-store = multi order) |
| subtotal / shipping_fee / discount / total | decimal | |
| address_id | bigint FK | alamat kirim |
| status | enum | pending_payment / confirmed / processed / shipped / delivered / completed / cancelled / refunded |
| escrow_status | enum | held / released / refunded |
| paid_at / shipped_at / completed_at | datetime | |

**order_items**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | bigint FK | |
| product_id | bigint FK | |
| variant_id | bigint FK null | |
| qty | int | |
| unit_price / total | decimal | snapshot harga |

**payments**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | bigint FK | |
| method | enum | wallet / va / qris / ewallet / cod |
| gateway_ref | varchar | nomor referensi |
| amount | decimal | |
| status | enum | pending / success / failed / refunded |
| paid_at | datetime | |

**wallets**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| user_id | bigint FK unique | |
| balance | decimal(14,2) | saldo aktif |
| escrow_balance | decimal(14,2) | dana ditahan |

**wallet_transactions**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| wallet_id | bigint FK | |
| type | enum | topup / payment / escrow_release / withdraw / refund / commission |
| amount | decimal (±) | |
| ref_id | bigint nullable | pesanan/withdraw terkait |
| balance_after | decimal | snapshot saldo |
| created_at | datetime | |

**withdraws**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| user_id | bigint FK | |
| amount | decimal | |
| bank / account_number / account_name | varchar | |
| status | enum | pending / processed / rejected | |

**shipments**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | bigint FK | |
| courier | varchar | ekspedisi |
| service | varchar | |
| tracking_number | varchar | |
| cost | decimal | |
| status / history | varchar / json | lacak |

**reviews**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_item_id | bigint FK | terikat pesanan selesai |
| user_id / product_id / store_id | FK | |
| rating | tinyint 1–5 | |
| comment | text | |
| status | enum | visible / hidden |

**conversations / messages**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| order_id | FK orders (nullable) | terisi bila percakapan dari pesanan |
| product_id | FK products (nullable) | terisi bila percakapan pra-pesanan dari detail produk |
| buyer_id | FK users (nullable) | pembeli pemilik percakapan pra-pesanan |
| message | text | |
| read_at | datetime | |

**categories**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | int PK | |
| name / slug / parent_id | varchar / int | hierarki kategori produk |

**coupons**
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | bigint PK | |
| code | varchar unique | |
| type | enum | percent / fixed |
| value | decimal | |
| store_id | FK null | platform atau per toko |
| max_usage / valid_from / valid_until | int / date | |

**settings** — key/value: komisi default, fee withdraw, integrasi gateway, opsi ongkir.

### 5.3 Implementasi Aktual (Iterasi 1)

Tabel yang terimplementasi (SQLAlchemy, PostgreSQL): `users`, `addresses`,
`categories`, `stores`, `products`, `cart_items`, `orders`, `order_items`,
`order_status_history`, `wallets`, `wallet_transactions`, `withdrawals`,
`reviews`, `conversations`, `messages`, `settings`.

Penyesuaian dari desain awal pada iterasi ini:

- **Escrow tanpa tabel `payments`** — status pembayaran diwakili `orders.escrow_status`
  (`held / released / refunded`) dan saldo escrow disimpan di `wallets.escrow_balance`;
  pembayaran hanya via wallet internal (payment gateway eksternal = rencana lanjutan).
- **Ongkir berbasis tier** — `settings.ONGKIR_TIER_A/B/C` (mis. 10.000 / 15.000 / 25.000)
  ditentukan dari provinsi alamat pembeli vs toko; ekspedisi pihak ketiga = rencana lanjutan.
- **Komisi platform** — `settings.COMMISSION_RATE` (default 5%); dipotong saat escrow
  dirilis ke penjual (wallet balance penjual = 95% dari total).
- **Riwayat status** — `order_status_history` mencatat perubahan status order (audit trail).
- **Belum diimplementasikan (rencana lanjutan)**: `product_variants`, `coupons`,
  tabel `payments`/`shipments` terpisah, notifikasi push/email, verifikasi keanggotaan
  Pramuka (nomor KWK), serta ekspor laporan CSV.

---

## 6. Desain API / Routing

Pola API RESTful (JSON), seluruh endpoint di bawah prefix `/api`. Implementasi Iterasi 1:

### Halaman Publik
| Metode | Route | Fungsi |
|---|---|---|
| GET | `/api/categories` | Daftar kategori produk |
| GET | `/api/cities` | Daftar kota toko aktif (saran lokasi pencarian) |
| GET | `/api/products` | Katalog + filter (q, city **parsial-match**, category, min/max price, sort: newest/cheapest/expensive/bestseller/**rating**/**reviewed** v1.9, page, size) |
| GET | `/api/products/suggest` | Saran produk saat mengetik (q, limit ≤10; nama cocok, urut terlaris) — v1.8 |
| GET | `/api/products/{slug}` | Detail produk + rating + ulasan |
| GET | `/api/stores/{slug}` | Halaman toko publik + produk toko |

### Akun & Autentikasi
| Metode | Route | Fungsi |
|---|---|---|
| POST | `/api/auth/register` | Registrasi (anggota/umum), password ≥ 8 |
| POST | `/api/auth/login` | Login → JWT |
| GET | `/api/auth/me` | Data user + wallet + store (SSO) |
| PUT | `/api/me` | Update profil |
| GET/POST/PUT/DELETE | `/api/me/addresses[/{id}]` | Multi-alamat pengiriman |

### Belanja
| Metode | Route | Fungsi |
|---|---|---|
| GET/POST | `/api/cart` `/api/cart/items` | Lihat / tambah item (grup per toko) |
| PUT/DELETE | `/api/cart/items/{id}` | Ubah qty / hapus item |
| POST | `/api/cart/checkout` | Buat order per toko + ongkir (tier A/B/C sesuai provinsi) |
| GET | `/api/orders` | Daftar pesanan saya (filter status) |
| GET | `/api/orders/{code}` | Detail pesanan (akses: pembeli/penjual/admin) |
| POST | `/api/orders/{code}/pay` | Bayar dari wallet → escrow |
| POST | `/api/orders/{code}/cancel` | Batalkan (refund bila sudah bayar) |
| POST | `/api/orders/{code}/confirm-receipt` | Konfirmasi terima → escrow release − komisi |

### Wallet & Pembayaran (escrow internal)
| Metode | Route | Fungsi |
|---|---|---|
| GET | `/api/wallet` | Saldo, escrow, mutasi |
| POST | `/api/wallet/topup` | Top-up (mock payment) |
| POST | `/api/wallet/withdrawals` | Ajukan pencairan (saldo ditahan) |
| GET | `/api/wallet/withdrawals` | Riwayat pencairan saya |
| GET | `/api/wallet/seller/withdrawals` | Riwayat pencairan toko saya |
| POST | `/api/admin/withdrawals/{id}/approve\|reject` | Proses pencairan (admin) |

### Penjual (Toko)
| Metode | Route | Fungsi |
|---|---|---|
| GET/POST/PUT | `/api/seller/store` | Lihat / ajukan / kelola toko (status pending→active) |
| GET/POST | `/api/seller/products` | Daftar / tambah produk (draft/active/archived) |
| GET/PUT/DELETE | `/api/seller/products/{id}` | Detail / update / hapus produk |
| GET | `/api/seller/orders` | Pesanan masuk (filter status) |
| GET | `/api/seller/orders/{id}` | Detail pesanan toko saya |
| POST | `/api/seller/orders/{id}/confirm` | Konfirmasi pesanan dibayar |
| POST | `/api/seller/orders/{id}/ship` | Kirim + nomor resi |
| GET | `/api/seller/dashboard` | Statistik toko (produk, pesanan, total penjualan, saldo) |

### Ulasan & Chat
| Metode | Route | Fungsi |
|---|---|---|
| POST | `/api/reviews` | Ulasan per item pesanan selesai (rating 1–5, UI bintang v1.7) |
| POST | `/api/conversations` | Mulai chat ke penjual dari produk (pra-pesanan, idempotent) |
| GET | `/api/conversations` | Daftar percakapan milik saya (pesan terakhir, unread, peran saya `i_am_seller`, urut aktivitas) |
| GET/POST | `/api/conversations/{id}/messages` | Baca (tandai dibaca) / kirim pesan (pembeli–penjual–admin) |

### Admin
| Metode | Route | Fungsi |
|---|---|---|
| GET/POST/PUT | `/api/admin/users` | Kelola user (role, aktif/nonaktif) |
| DELETE | `/api/admin/users/{id}` | Hapus permanen; otomatis nonaktif (soft delete) bila user masih punya data transaksi (order/keranjang/toko) — login user nonaktif ditolak |
| GET | `/api/admin/stores` | List toko |
| POST | `/api/admin/stores/{id}/approve\|reject\|suspend\|activate` | Moderasi toko |
| GET | `/api/admin/products` | List produk |
| POST | `/api/admin/products/{id}/deactivate` | Nonaktifkan produk |
| GET | `/api/admin/orders` | Semua pesanan |
| GET | `/api/admin/carts` | Status keranjang setiap user (item, qty, subtotal, updated_at) — admin/staff |
| GET | `/api/admin/reports` | Laporan (user, toko, produk, order per status, volume) |
| GET | `/api/admin/withdrawals` | List pencairan + approve/reject |

RBAC (v1.4): seluruh endpoint admin (`get_current_admin` & `require_staff_or_admin`)
menerima role `admin` atau `staff`; role `member` tetap ditolak (403).

Media (v1.3, dilengkapi v1.10): file gambar produk disajikan sebagai aset statis
lokal dari `frontend/public/images/products/` (path relatif disimpan pada kolom
`images`), termasuk gambar demo seed — produk barang (kue kering, keripik
pisang, es kopi, gelang tali kur, tote bag) dan produk jasa baru (fotografi,
desain logo, sewa tenda, masing-masing 1 gambar `jasa-*.jpg`); foto hero landing
disimpan di `frontend/public/images/hero-ig.png`. (CDN eksternal
`cdn.javascout.id` tetap rencana pengembangan lanjutan.)

---

## 7. Desain Antarmuka (UI/UX)

### 7.1 Struktur Aplikasi (PWA)
1. **Beranda**: header (logo, pencarian, login/keranjang), banner promosi, kategori populer, produk unggulan, toko pilihan, program "UMKM Pramuka".
2. **Katalog**: filter (kategori, harga, lokasi, rating), sorting (terlaris/terbaru/termurah), grid produk.
 3. **Detail Produk**: galeri gambar, harga, varian, stok, bintang rating rata-rata, ulasan per item (bintang readonly), tombol "Beli"/"Keranjang", info toko & ongkir, chat penjual.
 4. **Toko**: header toko (logo, nama, rating, alamat), produk toko, tombol chat.
 5. **Keranjang**: grup per toko, subtotal, lanjut checkout.
 6. **Checkout**: alamat, pilih kurir + ongkir, kupon, ringkasan, pilih pembayaran.
 7. **Order**: daftar & detail status, tracking resi, tombol konfirmasi terima, form ulasan bintang (klik 1–5) setelah pesanan selesai.
8. **Wallet**: saldo, top-up, mutasi, pencairan.
9. **Dashboard Penjual**: ringkasan penjualan, kelola produk/pesanan/kupon, pengaturan toko.
10. **Admin**: moderasi, laporan, pengaturan.
11. **Profil**: data anggota, verifikasi Pramuka, alamat, notifikasi.

### 7.2 Kerangka Desain
- Tema superapps modern: warna identitas Pramuka (merah-kuning/tua) dengan aksen hijau ekonomi.
- Komponen: kartu produk (foto, harga, rating, tombol), stepper checkout, status chip, bottom navigation (mobile), drawer admin.
- Ikon tombol WhatsApp & notifikasi konsisten di seluruh halaman.

### 7.3 Implementasi UI Iterasi 1

- **Navigasi superapp**: sidebar admin berisi Dashboard, Manajemen User, dan seksi
  **Marketplace** (Moderasi Toko, Produk, Pesanan, Keranjang Belanja, Penarikan
  Dana, Laporan); sidebar akun pengguna berisi Belanja (Katalog, Keranjang,
  Pesanan, Wallet, Profil) dan — hanya bila punya toko aktif — Toko Saya (Toko,
  Dashboard Penjual, Produk, Pesanan Masuk, Pencairan Dana).
  Modul superapp lain (Berita, Anggota, Kegiatan, Galeri, Dokumen, Pengaturan)
  ditandai "Segera Hadir".
- **Login & redirect berbasis role** (v1.4): halaman login berjudul "Masuk"
  (tidak lagi "Masuk Admin") dan setelah login mengarahkan sesuai peran —
  admin/staff → `/admin`, member dengan toko aktif → `/account/seller/dashboard`,
  member biasa → `/catalog`; pengguna yang sudah login membuka `/login` dialihkan
  ke tujuan perannya; rute `/account/seller/*` dilindungi `requiresSeller`
  (tanpa toko aktif → dialihkan ke Keranjang); role `staff` dianggap operator
  back-office (menu & API admin, backend `get_current_admin` menerima admin/staff),
  role `member` ditolak dari area admin (403).
- **Halaman Keranjang Belanja** (admin, v1.4): tabel seluruh user dengan chip
  produk di keranjang ("2× Kue Kering"), total item, subtotal, waktu terakhir
  diubah, dan badge status Berisi/Kosong; sumber data `GET /api/admin/carts`
  (bisa diakses admin & staff).
- **Topbar & footer publik** (v1.3): topbar berisi logo ⚜️ + nama "JavaScout
  Pramuka Jabar", tautan Katalog Marketplace, tombol Masuk (outline) dan Daftar
  (solid); footer gelap berisi brand, tautan cepat, dan hak cipta.
- **Landing page** (redesain v1.3): hero dua tahap — foto resmi Pramuka Jawa
  Barat (dari media sosial @pramukajabar, disimpan lokal) sebagai latar dengan
  overlay coklat transparan agar teks terbaca; logo lingkaran berbingkai emas;
  judul "SuperApps Pramuka Jawa Barat"; **kolom pencarian pill** (v1.5, diperluas
  v1.6 dengan kolom **kota**) di bawah deskripsi — kirim ke `/catalog?q=…&city=…`;
  CTA "Jelajahi Katalog" (emas) dan
  "Daftar Gratis" (ghost); strip statistik melayang (produk, toko aktif, escrow,
  layanan); 4 kartu fitur (Katalog, Wallet & Escrow, Buka Toko, Chat Penjual);
  kartu kategori populer yang menuju katalog dengan filter aktif; band CTA
  maroon "Daftar & Buka Toko". Katalog dapat diakses publik tanpa login.
- **Katalog marketplace** (redesain Iterasi 1): hero gradient coklat→maroon dengan
  aksen emas + judul & badge keranjang; **kartu kategori** berikon (termasuk
  kartu **"Semua Barang"** v1.10 berikon toko untuk menampilkan seluruh produk;
  makanan, minuman, kerajinan, fashion, jasa, lainnya) yang dapat diklik untuk
  memfilter grid;
  **panel samping** (v1.10) berisi blok Pencarian (`SearchSuggest`) dan blok
  Filter (kategori, **lokasi** — partial-match + saran kota dari
  `/api/cities`, urutan — termasuk **Termurah/Termahal** v1.6 serta **Rating
  Tertinggi & Terbanyak Diulas** v1.9); penghitung hasil; grid kartu produk
  responsif (min 240px) — gambar rasio 4:3 dengan efek zoom saat hover, badge
  "Stok Habis", nama maks 2 baris, rating bintang emas, harga maroon tebal, tombol
  "+ Tambah ke Keranjang" full-width (berubah "Menambahkan…" → "✓ Ditambahkan"
  saat diproses, disertai **toast** konfirmasi dan cegah klik ganda); pagination
  (‹ Sebelumnya / Berikutnya ›); state kosong yang informatif.
- **Rating bintang** (v1.7): komponen `StarRating.vue` dua mode — input
  interaktif (klik bintang 1–5) pada form ulasan di detail pesanan, readonly
  pada detail produk (per ulasan + ringkasan rata-rata) dan kartu produk.
- **Saran pencarian** (v1.8): komponen `SearchSuggest.vue` di kolom pencarian
  landing page & katalog — dropdown saran produk serupa saat mengetik (nama,
  gambar, harga, toko, jumlah terjual; navigasi keyboard; pilih → detail produk).
- **Urutkan berdasarkan ulasan** (v1.9): opsi dropdown "Rating Tertinggi"
  (rata-rata bintang terbaik) & "Terbanyak Diulas" (jumlah ulasan terbanyak)
  pada baris filter katalog.
- **Skema warna**: coklat `#5c4033`, maroon `#7b241c`, emas `#d4ac0d`, krem `#faf6f0`
  (token CSS `--brown`, `--maroon`, `--gold`, `--cream`).

### 7.4 Wireframe Beranda (deskripsi)
```
┌──────────────────────────────────────────────────┐
│ Logo JavaScout | Cari produk | Keranjang | Login │
├──────────────────────────────────────────────────┤
│ BANNER: "Buka Toko Gratis — Program UMKM Pramuka"│
├──────────────────────────────────────────────────┤
│ Kategori: Makanan | Kerajinan | Pakaian | ...    │
├──────────────────────────────────────────────────┤
│ Produk Unggulan (grid)                           │
├──────────────────────────────────────────────────┤
│ Toko Pilihan (kartu toko + rating)               │
├──────────────────────────────────────────────────┤
│ Program UMKM Pramuka (banner + CTA)              │
├──────────────────────────────────────────────────┤
│ Footer: Tentang | Bantuan | Syarat | Kontak      │
└──────────────────────────────────────────────────┘
```

---

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

## 10. Pengujian

**Terimplementasi (pytest + TestClient, 78 test lulus):**
1. **Unit/Integration (API level)**: auth (registrasi, login, akses), toko & produk
   (katalog, filter q/kategori/lokasi parsial, sort termurah–termahal, **sort
   rating tertinggi & terbanyak diulas v1.9** — urut rata-rata bintang/jumlah
   ulasan visible dengan produk tanpa ulasan di akhir, **saran
   pencarian `/api/products/suggest`** — hasil cocok kata kunci, batas limit,
   kosong tanpa hasil, 422 tanpa q, seller CRUD,
   moderasi admin), keranjang (lintas toko, stok,
   produk non-aktif), checkout (alamat wajib, ongkir per tier provinsi, pengurangan
   stok), order (bayar, escrow, double-pay ditolak, cancel/refund, akses kontrol,
   alur lengkap penjual s.d. komisi), wallet (top-up, mutasi, withdraw +
   approve/reject, saldo penjual bertambah 95%), ulasan (setelah selesai, duplikat
   ditolak, rating 1–5, tampil di detail produk), chat (auto-buat saat checkout,
   akses peserta), admin (moderasi toko/produk, RBAC admin+staff, monitor
   keranjang user, laporan, dashboard penjual).
2. **UI (manual, per fitur)**: rating bintang — input klik 1–5 di form ulasan
   detail pesanan (menggantikan dropdown), tampilan readonly di detail produk
   (per ulasan + rata-rata) dan kartu katalog; flow teruji: pesanan completed →
   ulasan 4★/5★ → rating produk terbarui di katalog & detail.

**Rencana pengujian lanjutan:**
1. Unit test service level (harga, escrow, wallet) secara terisolasi.
2. UAT: onboarding penjual, belanja lintas toko, pencairan dana, chat.
3. Performance Test: beban katalog & checkout; Lighthouse ≥ 80.
4. Security Test: OWASP ZAP, uji pembayaran (double-charge), injeksi, brute-force, otorisasi lintas toko.
5. Responsive Test: mobile/tablet/desktop, PWA installability.

---

## 11. Rencana Pengembangan Lanjutan

1. Aplikasi mobile native (Android/iOS) — superapp di perangkat.
2. Modul Koperasi & Simpan Pinjam (usaha kwartir).
3. Modul Edukasi & Sertifikasi (e-learning kewirausahaan Pramuka).
4. Modul Event & Pendaftaran kegiatan (bazar, lomba wirausaha).
5. Analitik penjualan & dashboard Kwartir (laporan ekonomi daerah).
6. Logistik bersama (penggabungan pengiriman antar-toko).
7. Program pembinaan UMKM: kurasi produk, pelatihan, pendampingan.
8. Fitur komunitas: forum, feed kegiatan ekonomi anggota.

---

## 12. Lampiran

- A. Peta navigasi aplikasi (sitemap).
- B. Daftar kategori produk awal.
- C. Daftar pangkalan/Kwartir untuk verifikasi keanggotaan.
- D. Glossary istilah e-commerce & kepramukaan.
