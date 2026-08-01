# Implementation Plan
## Modul: Data Potensi Keanggotaan (Gerakan Pramuka)

Setiap task merujuk ke requirement terkait dari `requirements.md` (kode FR-x).

- [ ] 1. Setup proyek & integrasi awal ke Kwarda SuperApp
  - [ ] 1.1 Konfirmasi kontrak integrasi dengan tim Core SuperApp: format token/JWT, cara membaca klaim peran & wilayah, API/skema akses ke master data `wilayah` dan `gudep`
  - [ ] 1.2 Inisialisasi repo modul (backend service + micro-frontend/module route `/keanggotaan/*`), mengikuti konvensi mono-repo/poly-repo SuperApp yang berlaku
  - [ ] 1.3 Konfigurasi database PostgreSQL (skema `keanggotaan`) & migration tool (mis. Prisma/Knex/TypeORM); tentukan apakah 1 instance DB shared dengan modul lain atau DB terpisah per service
  - [ ] 1.4 Setup environment (.env), CI/CD, dan pendaftaran modul ini ke API Gateway/menu registry SuperApp
  - _Requirements: NFR performa & skalabilitas; konteks integrasi SuperApp_

- [ ] 2. Skema data domain Keanggotaan
  - [ ] 2.1 Integrasikan referensi ke `wilayah` & `gudep` milik Core (via FK lintas skema atau pemanggilan API Core — bukan membuat tabel baru)
  - [ ] 2.2 Buat tabel `anggota` dengan enum jenjang & validasi rentang usia per jenjang
  - [ ] 2.3 Buat tabel `riwayat_jenjang`
  - [ ] 2.4 Buat tabel `kompetensi_master`, `capaian_kompetensi`, `potensi_minat` (domain modul ini)
  - _Requirements: FR-1_

- [ ] 3. Integrasi Autentikasi & Akses (delegasi ke Core)
  - [ ] 3.1 Implementasi middleware verifikasi token JWT yang diterbitkan **Core Auth Service** (bukan membuat sistem login baru)
  - [ ] 3.2 Implementasi middleware RBAC (5 peran) dan data-scoping wilayah/gudep berdasarkan klaim token
  - [ ] 3.3 Pendaftaran grup menu "Keanggotaan" & submenunya ke menu registry SuperApp (menu dinamis berbasis peran)
  - [ ] 3.4 Implementasi pencatatan `log_audit` domain Keanggotaan, dengan opsi kirim event ke layanan log audit terpusat SuperApp
  - _Requirements: FR-5, FR-6_

- [ ] 4. Manajemen Profil Anggota (CRUD)
  - [ ] 4.1 Endpoint & form tambah/ubah anggota, termasuk atribut spesifik jenjang
  - [ ] 4.2 Validasi usia vs jenjang dengan warning non-blocking
  - [ ] 4.3 Fitur mutasi/kenaikan jenjang beserta pencatatan riwayat
  - [ ] 4.4 Fitur upload & pengelolaan foto profil (object storage)
  - [ ] 4.5 Atribut tambahan untuk Anggota Dewasa (peran, sertifikasi kursus)
  - _Requirements: FR-1_

- [ ] 5. Pencarian & Filter Data
  - [ ] 5.1 Endpoint pencarian dengan indeks pada nama/NTA/gudep
  - [ ] 5.2 UI filter kombinasi (jenjang, gender, wilayah, status, usia)
  - [ ] 5.3 Fitur ekspor hasil pencarian ke Excel & PDF
  - [ ] 5.4 Penerapan data-scoping otomatis sesuai peran pengguna
  - _Requirements: FR-2_

- [ ] 6. Pemetaan Kompetensi & Potensi
  - [ ] 6.1 Buat tabel & master data `kompetensi_master` (SKU/SKK/TKK per jenjang)
  - [ ] 6.2 Endpoint & UI pencatatan `capaian_kompetensi` oleh Pembina
  - [ ] 6.3 Logika otomatis deteksi kelengkapan tingkat & notifikasi kenaikan
  - [ ] 6.4 Endpoint & form pencatatan `potensi_minat` (kategori bebas)
  - [ ] 6.5 Visualisasi radar chart profil kompetensi individu
  - [ ] 6.6 Rekap agregat kompetensi per gudep
  - _Requirements: FR-3_

- [ ] 7. Rekapitulasi & Pelaporan
  - [ ] 7.1 Query agregasi rekursif wilayah → gudep → anggota
  - [ ] 7.2 Dashboard ringkasan jumlah anggota per jenjang/wilayah/gender
  - [ ] 7.3 Grafik tren pertumbuhan anggota per periode
  - [ ] 7.4 Generator laporan periodik (bulanan/tahunan)
  - [ ] 7.5 Fitur ekspor laporan ke PDF & Excel siap cetak
  - _Requirements: FR-4_

- [ ] 8. Impor Data Massal
  - [ ] 8.1 Buat template Excel impor anggota
  - [ ] 8.2 Endpoint impor dengan validasi baris & laporan error parsial
  - [ ] 8.3 UI unggah file & tampilan hasil impor (sukses/gagal per baris)
  - _Requirements: FR-5_

- [ ] 9. Navigasi & Integrasi Submenu ke Shell SuperApp
  - [ ] 9.1 Implementasi grup submenu "Keanggotaan" (Dashboard, Data Anggota, Pemetaan Kompetensi, Rekapitulasi & Laporan, Administrasi Keanggotaan) yang menempel pada shell/layout global SuperApp
  - [ ] 9.2 Rendering menu dinamis berbasis role pengguna, dikoordinasikan dengan menu registry Core
  - [ ] 9.3 Breadcrumb navigasi lintas SuperApp (`SuperApp / Keanggotaan / ...`) di setiap halaman
  - [ ] 9.4 Responsive layout mengikuti shell SuperApp untuk desktop & mobile
  - [ ] 9.5 Sediakan API internal data dasar anggota (nama, NTA, jenjang, gudep) untuk dikonsumsi modul lain (mis. Keuangan/Iuran, Kegiatan)
  - _Requirements: FR-6_

- [ ] 10. Keamanan & Kepatuhan
  - [ ] 10.1 Enkripsi kolom data sensitif (kontak/alamat) at-rest
  - [ ] 10.2 Konfigurasi HTTPS/TLS end-to-end
  - [ ] 10.3 Signed URL sementara untuk akses foto/dokumen
  - [ ] 10.4 Rate limiting pada endpoint login & impor
  - _Requirements: NFR Keamanan & Kepatuhan_

- [ ] 11. Pengujian & Quality Assurance
  - [ ] 11.1 Unit test untuk validasi model data (jenjang, usia, kompetensi)
  - [ ] 11.2 Integration test untuk alur RBAC & data-scoping
  - [ ] 11.3 Uji performa pencarian dengan dataset simulasi 100.000 anggota
  - [ ] 11.4 User Acceptance Test (UAT) bersama perwakilan Admin Gudep/Kwartir

- [ ] 12. Deployment & Dokumentasi
  - [ ] 12.1 Setup deployment (staging & production)
  - [ ] 12.2 Dokumentasi teknis API & panduan pengguna per peran
  - [ ] 12.3 Pelatihan penggunaan sistem untuk Admin Gudep/Kwartir/Pembina
