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
- **Implementasi v1.17**: notifikasi in-app — tabel `notifications` (user_id,
  tipe order/chat, judul, isi, link, dibaca); pemicu otomatis: pesanan baru &
  dibayar (ke penjual), diproses & dikirim + resi & dibatalkan & selesai +
  escrow dirilis (ke pembeli/penjual sesuai peran), pesan chat baru (ke lawan
  bicara); API `GET /api/notifications` (30 terbaru), `unread-count`,
  `read-all`, `{id}/read`; komponen `NotificationBell.vue` — lonceng dengan
  badge jumlah belum dibaca (polling 10 detik), dropdown daftar notifikasi
  (ikon per tipe, waktu relatif, sorotan belum dibaca, "Tandai semua dibaca",
  klik menuju halaman terkait) — dipasang di topbar halaman publik dan header
  sidebar akun.
- Notifikasi eksternal (push/email/WhatsApp) tetap rencana pengembangan lanjutan.

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

