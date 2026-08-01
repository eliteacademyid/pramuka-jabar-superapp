# Development Task Checklist (Task.md)
## Website Pramuka Kwarcab Kabupaten Bandung Barat (KBB)

---

### Fase 1: Perencanaan, Desain UI/UX & Arsitektur (Minggu 1)
- [ ] **1.1. Requirement & Research**
  - [x] Finalisasi dokumen SRS (requirements.md).
  - [ ] Analisis komparatif website `pramuka.or.id`, `pramukajabar.or.id`, dan portal modern lainnya.
  - [ ] Pengumpulan aset resmi (Logo Kwarcab KBB, Warna Identitas Coklat-Kuning-Merah, Foto Kegiatan HQ).
- [ ] **1.2. Design System & Wireframing**
  - [ ] Pembuatan Wireframe UI untuk Mobile & Desktop (Figma).
  - [ ] Pembuatan UI Design High-Fidelity & Prototyping (Clean, Modern Grid, Smooth Scroll).
  - [ ] Penentuan Palette Warna & Tipografi (Coklat Pramuka khas, Krem Accent, Navy/Dark Mode, Font Sans-serif Modern).
- [ ] **1.3. Architecture & Project Setup**
  - [ ] Setup repository Git (GitHub / GitLab).
  - [ ] Inisialisasi Project (Next.js/Laravel + Tailwind CSS).
  - [ ] Konfigurasi ESLint, Prettier, dan Tailwind Config.
  - [ ] Perancangan Skema Database (ERD) untuk Berita, Agenda, Pengurus, Dokumen, Galeri.

---

### Fase 2: Pengembangan Frontend - Public Portal (Minggu 2 - 3)
- [ ] **2.1. Layout Utama & Components**
  - [ ] Navbar / Header (Responsive, Sticky, Mobile Drawer Navigation, Quick Search).
  - [ ] Footer (Sosial Media, Alamat, Quick Links, Copyright, Badge WOSM).
  - [ ] Dark Mode / Light Mode Toggle.
- [ ] **2.2. Halaman Beranda (Homepage)**
  - [ ] Hero Banner Carousel / Swiper.js.
  - [ ] Widget Statistik Interaktif (Counter Up Animation).
  - [ ] Section Berita Terbaru & Pengumuman (Card Layout + Filter Kategori).
  - [ ] Section Agenda Kegiatan Terdekat (Calendar Badge View).
  - [ ] Section Galeri Multimedia Grid & Video Embed.
  - [ ] Sambutan Ketua Kwarcab KBB Card Component.
- [ ] **2.3. Halaman Profil Kwarcab**
  - [ ] Halaman Sambutan & Visi-Misi.
  - [ ] Halaman Sejarah & Arti Logo/Lambang.
  - [ ] Halaman Struktur Organisasi (Interactive Tree Chart / Grid Pengurus).
  - [ ] Halaman Daftar Kwarran KBB (Accordion / Interactive Map View 16 Kecamatan).
- [ ] **2.4. Halaman Berita & Artikel**
  - [ ] Halaman Listing Berita (Pagination, Search Bar, Category Filter).
  - [ ] Halaman Detail Berita (Breadcrumb, Content Styling, Social Share Buttons, Related Posts).
- [ ] **2.5. Halaman Organisasi & Badan Kelengkapan**
  - [ ] Sub-page DKC Bandung Barat.
  - [ ] Sub-page Pusdiklatcab KBB (Info Kursus & Pelatihan).
  - [ ] Sub-page Satuan Karya (SAKA) & SAKO.
- [ ] **2.6. Halaman Layanan, Pustaka & Galeri**
  - [ ] Halaman Pustaka Dokumen (Download Table/List with PDF Viewer & Search).
  - [ ] Halaman Integrasi E-Services / KTA Online Info Page.
  - [x] Halaman e-Pelatihan (Daftar Pelatihan, Ruang Belajar, Kuis, Hasil & Sertifikat).
  - [ ] Halaman Galeri Foto & Video (Lightbox Gallery).
  - [ ] Halaman Kontak & Maps (Form Kontak + Google Maps Embed).

---

### Fase 3: Pengembangan Backend & Admin Panel (Minggu 4 - 5)
- [ ] **3.1. Database & Authentication API**
  - [ ] Setup Database Tables & Migrations.
  - [ ] Auth System (Login, Logout, Reset Password, JWT/Session Auth).
  - [ ] Middleware RBAC (Role-Based Access Control).
- [ ] **3.2. API Management Content (CRUD)**
  - [ ] API Berita & Pengumuman (Upload Thumbnail, Rich Text Editor Support).
  - [ ] API Agenda Kegiatan.
  - [x] API e-Pelatihan (Modul Pelatihan, Materi, Kuis, Progress Tracking, Certificate Generator).
  - [ ] API Dokumen & File Download.
  - [ ] API Galeri Foto/Video.
  - [ ] API Struktur Pengurus & Kwarran.
- [ ] **3.3. Dashboard Admin UI (CMS)**
  - [ ] Layout Admin Dashboard (Sidebar, Header, Analytics Cards).
  - [ ] Halaman Pengelolaan Berita & Artikel (WYSIWYG Editor Integration).
  - [ ] Halaman Pengelolaan Agenda & Events.
  - [ ] Halaman Pengelolaan e-Pelatihan (Manajemen Pelatihan, Materi, Kuis, Data Peserta).
  - [ ] Halaman Pengelolaan Dokumen & File.
  - [ ] Halaman Pengelolaan Galeri & Media Library.
  - [ ] Halaman Pengaturan Website (Header, Footer, Sosmed, Metadata).

---

### Fase 4: Pengujian, Optimasi & Deployment (Minggu 6)
- [ ] **4.1. Quality Assurance & Testing**
  - [ ] Testing Responsive View (Mobile, Tablet, Desktop).
  - [ ] Cross-Browser Compatibility Testing (Chrome, Safari, Firefox, Edge).
  - [ ] Cross-Device Performance & Speed Optimization.
  - [ ] Security Audit (Input Sanitization, Upload Validation, Protection against XSS/CSRF).
- [ ] **4.2. SEO & Accessibility**
  - [ ] Meta Tag & Open Graph Setup untuk semua halaman.
  - [ ] Generasi Dynamic Sitemap XML & Robots.txt.
  - [ ] Pengujian Aksesibilitas (WCAG Compliance Check).
- [ ] **4.3. Deployment & Go-Live**
  - [ ] Deploy Database & Backend Server.
  - [ ] Deploy Frontend Client (Vercel / Cloud VPS).
  - [ ] Setup Domain Resmi Kwarcab KBB (misal: `pramuka-kbb.or.id` atau `kwarcabkbb.or.id`).
  - [ ] Setup SSL Certificate (HTTPS).
  - [ ] Penyerahan Dokumentasi System & User Manual Admin.