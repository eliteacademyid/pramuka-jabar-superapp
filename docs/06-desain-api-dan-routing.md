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

