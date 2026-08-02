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
> Pembaruan v1.15: **kategori Perlengkapan Pramuka** — kategori baru dengan
> 3 produk contoh di toko demo: Set Seragam Pramuka Lengkap (Rp185.000/set),
> Tongkat Pramuka Kayu (Rp45.000/batang), Bendera Semaphore Pasang
> (Rp30.000/pasang), lengkap dengan ilustrasi SVG lokal
> (`frontend/public/images/products/perlengkapan-*.svg`); ikon kategori baru
> (fa-campground) di katalog & landing; 82 test otomatis.
> Pembaruan v1.16: **kategori Peralatan Berkemah** — kategori baru (slug
> `camping`, ikon fa-tent) dengan 3 produk contoh: Tenda Dome Camping 4 Orang
> (Rp450.000/unit), Sleeping Bag Pramuka (Rp150.000/pcs), Kompor Portable
> Camping (Rp120.000/unit), ilustrasi SVG lokal
> (`frontend/public/images/products/camping-*.svg`).
> Pembaruan v1.17: **sistem notifikasi in-app** — tabel `notifications` +
> `GET /api/notifications`, `GET /api/notifications/unread-count`, `POST
> /api/notifications/read-all`, `POST /api/notifications/{id}/read`;
> notifikasi otomatis untuk: pesanan baru, dibayar, diproses, dikirim (dengan
> resi), dibatalkan, selesai & escrow dirilis (ke penjual/pembeli sesuai
> peran), serta pesan chat baru ke lawan bicara; komponen `NotificationBell.vue`
> (lonceng + badge unread + dropdown daftar, polling 10 detik, tandai semua
> dibaca) dipasang di topbar halaman publik & header sidebar akun; 87 test
> otomatis.
> Pembaruan v1.18: **ticketing perselisihan penjual–pembeli** — tabel
> `tickets`, `ticket_messages`, `ticket_status_history`; pembeli/penjual dari
> pesanan yang sudah dibayar dapat membuka tiket (`POST /api/tickets`, maks.
> 1 tiket aktif per pesanan, kode `TKT-XXXXXXXX`), balas pesan, dan menutup
> tiket sendiri; admin meninjau (`in_review`), menyelesaikan (`resolved`),
> atau menutup (`closed`) dengan catatan; setiap perubahan status tercatat di
> riwayat beserta pelaku & waktu (status tracking + history transaksi); notifikasi
> otomatis ke kedua pihak & admin; halaman `/account/tickets` (daftar, buat
> tiket dari detail pesanan, detail dgn thread + timeline status) dan
> `/admin/tickets`; 94 test otomatis.
> Pembaruan v1.19: **filter katalog pindah di samping pencarian** — toolbar
> tunggal di bawah banner: pil pencarian + select kategori + input lokasi +
> select urutkan + tombol Cari sejajar; panel samping katalog dihapus.
> Pembaruan v1.20: **sistem tema per-user** — pilihan **Default** (terang),
> **Gelap** (dark), dan **Biru cerah** (blue); preferensi disimpan per akun
> (kolom `users.theme`, endpoint `GET/PUT /api/me/theme`) dan tersinkron otomatis
> ke server setelah login; dipasang sebagai menu dropdown di topbar halaman
> publik (landing & marketplace) serta sidebar akun & admin; tema diterapkan
> seketika via kelas `dark`/`blue` pada root dokumen (localStorage cache + anti
> flash), seluruh palet warna (cokelat/merah/emas) diganti via CSS variable;
> 95 test otomatis.
> Pembaruan v1.21: **penyempurnaan tampilan landing & katalog** — foto hero
> landing di-blur + saturasi dilembutkan (filter `blur(6px) saturate(0.45)` di
> lapisan terpisah dengan overlay gradasi & text-shadow agar teks lega); kartu
> fitur/kategori/statistik & CTA lebih lapang (radius, padding, shadow halus);
> teks kartu fitur disederhanakan; banner katalog dipangkas setengah tinggi;
> kartu kategori katalog diubah jadi **chip kompak satu baris** (ikon kecil +
> nama, tanpa deskripsi) sehingga hasil pencarian/produk langsung terlihat
> tanpa scroll.
> Pembaruan v1.22: **HTTPS untuk pengembangan lokal** — sertifikat lokal via
> **mkcert** (CA lokal, berlaku untuk `localhost`/`127.0.0.1`/`::1`), Vite dev
> server melayani `https://localhost:5173/`, folder `frontend/certs` di-mount
> ke container dan masuk `.gitignore`; backend tetap `http://localhost:8000`
> (localhost bebas dari pembatasan mixed-content di browser).
> Pembaruan v1.23: **Bantuan AI berbasis Gemini** — widget chat "Bantuan AI"
> di sidebar akun (tombol di sidebar-footer membuka panel mengambang di pojok
> kanan bawah); endpoint `POST /api/ai/chat` (auth member, pesan maks. 2000
> karakter) memanggil Google Gemini (`gemini-2.0-flash`, system prompt asisten
> marketplace JavaScout, jawaban Bahasa Indonesia) via `GEMINI_API_KEY` &
> `GEMINI_MODEL` di env; konteks user (nama, peran) disertakan; error ramah
> bila key belum dikonfigurasi (503) atau layanan terganggu (502); chip saran
> pertanyaan, indikator mengetik, riwayat percakapan per sesi; 100 test otomatis.
> Deskripsi pada dokumen ini mengikuti implementasi aktual pada bagian yang sudah
> dibangun; bagian lain (payment gateway, ekspedisi pihak ketiga, kupon, varian
> produk, notifikasi) tetap merupakan rencana pengembangan lanjutan.

---

