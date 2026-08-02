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

