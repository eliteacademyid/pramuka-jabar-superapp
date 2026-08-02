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

