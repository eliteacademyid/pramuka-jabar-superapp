import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../components/PublicLayout.vue'
import AdminLayout from '../components/AdminLayout.vue'
import KontributorLayout from '../components/KontributorLayout.vue'
import PenjualLayout from '../components/PenjualLayout.vue'
import Home from '../views/public/Home.vue'
import DataStatistik from '../views/public/DataStatistik.vue'
import LoginPage from '../views/public/LoginPage.vue'
import HubKegiatan from '../views/public/HubKegiatan.vue'
import HubKegiatanDetail from '../views/public/HubKegiatanDetail.vue'
import Marketplace from '../views/public/Marketplace.vue'
import ProdukDetail from '../views/public/ProdukDetail.vue'
import Checkout from '../views/public/Checkout.vue'
import UploadBukti from '../views/public/UploadBukti.vue'
import CekPesanan from '../views/public/CekPesanan.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'
import DataWilayah from '../views/admin/DataWilayah.vue'
import DataAnggota from '../views/admin/DataAnggota.vue'
import RekapStatistik from '../views/admin/RekapStatistik.vue'
import ProgramKerjaList from '../views/admin/ProgramKerjaList.vue'
import KegiatanList from '../views/admin/KegiatanList.vue'
import KalenderKegiatan from '../views/admin/KalenderKegiatan.vue'
import ModerasiHubKegiatan from '../views/admin/ModerasiHubKegiatan.vue'
import RekapKontribusi from '../views/admin/RekapKontribusi.vue'
import SuratMasukList from '../views/admin/SuratMasukList.vue'
import SuratMasukForm from '../views/admin/SuratMasukForm.vue'
import SuratMasukDetail from '../views/admin/SuratMasukDetail.vue'
import SuratKeluarList from '../views/admin/SuratKeluarList.vue'
import SuratKeluarForm from '../views/admin/SuratKeluarForm.vue'
import DisposisiSaya from '../views/admin/DisposisiSaya.vue'
import RekapPersuratan from '../views/admin/RekapPersuratan.vue'
import AlokasiAnggaranList from '../views/admin/AlokasiAnggaranList.vue'
import AlokasiAnggaranForm from '../views/admin/AlokasiAnggaranForm.vue'
import RealisasiAnggaranDetail from '../views/admin/RealisasiAnggaranDetail.vue'
import ReviewRealisasi from '../views/admin/ReviewRealisasi.vue'
import LaporanKegiatanList from '../views/admin/LaporanKegiatanList.vue'
import LaporanKegiatanForm from '../views/admin/LaporanKegiatanForm.vue'
import DashboardTransparansi from '../views/admin/DashboardTransparansi.vue'
import VerifikasiToko from '../views/admin/VerifikasiToko.vue'
import KategoriProdukList from '../views/admin/KategoriProdukList.vue'
import RekapMarketplace from '../views/admin/RekapMarketplace.vue'
import KontributorDashboard from '../views/kontributor/KontributorDashboard.vue'
import HubKegiatanSaya from '../views/kontributor/HubKegiatanSaya.vue'
import HubKegiatanForm from '../views/kontributor/HubKegiatanForm.vue'
import PenjualDashboard from '../views/penjual/PenjualDashboard.vue'
import TokoSaya from '../views/penjual/TokoSaya.vue'
import ProdukSaya from '../views/penjual/ProdukSaya.vue'
import ProdukForm from '../views/penjual/ProdukForm.vue'
import PesananMasuk from '../views/penjual/PesananMasuk.vue'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      { path: '', name: 'landing', component: Home },
      { path: 'data-kepramukaan', name: 'data-kepramukaan', component: DataStatistik },
      { path: 'login', name: 'login', component: LoginPage },
      { path: 'hub-kegiatan', name: 'hub-kegiatan', component: HubKegiatan },
      {
        path: 'hub-kegiatan/:id',
        name: 'hub-kegiatan-detail',
        component: HubKegiatanDetail
      },
      { path: 'marketplace', name: 'marketplace', component: Marketplace },
      {
        path: 'marketplace/produk/:id',
        name: 'marketplace-produk',
        component: ProdukDetail
      },
      { path: 'marketplace/checkout', name: 'marketplace-checkout', component: Checkout },
      { path: 'marketplace/bukti', name: 'marketplace-bukti', component: UploadBukti },
      { path: 'marketplace/cek', name: 'marketplace-cek', component: CekPesanan }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['admin', 'staff'] },
    children: [
      { path: '', name: 'admin-dashboard', component: Dashboard },
      { path: 'users', name: 'admin-users', component: Users },
      { path: 'wilayah', name: 'admin-wilayah', component: DataWilayah },
      { path: 'anggota', name: 'admin-anggota', component: DataAnggota },
      { path: 'rekap', name: 'admin-rekap', component: RekapStatistik },
      { path: 'program-kerja', name: 'admin-program-kerja', component: ProgramKerjaList },
      { path: 'kegiatan', name: 'admin-kegiatan', component: KegiatanList },
      { path: 'kalender', name: 'admin-kalender', component: KalenderKegiatan },
      { path: 'hub-moderasi', name: 'admin-hub-moderasi', component: ModerasiHubKegiatan },
      { path: 'hub-rekap', name: 'admin-hub-rekap', component: RekapKontribusi },
      { path: 'surat-masuk', name: 'admin-surat-masuk', component: SuratMasukList },
      { path: 'surat-masuk/baru', name: 'admin-surat-masuk-baru', component: SuratMasukForm },
      { path: 'surat-masuk/:id', name: 'admin-surat-masuk-detail', component: SuratMasukDetail },
      { path: 'surat-keluar', name: 'admin-surat-keluar', component: SuratKeluarList },
      { path: 'surat-keluar/baru', name: 'admin-surat-keluar-baru', component: SuratKeluarForm },
      { path: 'surat-keluar/:id', name: 'admin-surat-keluar-edit', component: SuratKeluarForm },
      { path: 'disposisi-saya', name: 'admin-disposisi-saya', component: DisposisiSaya },
      { path: 'persuratan-rekap', name: 'admin-persuratan-rekap', component: RekapPersuratan },
      { path: 'anggaran-alokasi', name: 'admin-anggaran-alokasi', component: AlokasiAnggaranList },
      { path: 'anggaran-alokasi/baru', name: 'admin-anggaran-alokasi-baru', component: AlokasiAnggaranForm },
      { path: 'anggaran-realisasi/:id', name: 'admin-anggaran-realisasi', component: RealisasiAnggaranDetail },
      { path: 'realisasi-review', name: 'admin-realisasi-review', component: ReviewRealisasi },
      { path: 'laporan-kegiatan', name: 'admin-laporan-kegiatan', component: LaporanKegiatanList },
      { path: 'laporan-kegiatan/baru', name: 'admin-laporan-kegiatan-baru', component: LaporanKegiatanForm },
      { path: 'laporan-kegiatan/:id/edit', name: 'admin-laporan-kegiatan-edit', component: LaporanKegiatanForm },
      { path: 'dashboard-transparansi', name: 'admin-dashboard-transparansi', component: DashboardTransparansi },
      { path: 'marketplace/verifikasi-toko', name: 'admin-marketplace-verifikasi', component: VerifikasiToko },
      { path: 'marketplace/kategori', name: 'admin-marketplace-kategori', component: KategoriProdukList },
      { path: 'marketplace/rekap', name: 'admin-marketplace-rekap', component: RekapMarketplace }
    ]
  },
  {
    path: '/kontributor',
    component: KontributorLayout,
    meta: { requiresAuth: true, roles: ['kontributor'] },
    children: [
      { path: '', name: 'kontributor-dashboard', component: KontributorDashboard },
      { path: 'saya', name: 'kontributor-saya', component: HubKegiatanSaya },
      { path: 'tulis', name: 'kontributor-tulis', component: HubKegiatanForm }
    ]
  },
  {
    path: '/penjual',
    component: PenjualLayout,
    meta: { requiresAuth: true, roles: ['penjual'] },
    children: [
      { path: '', name: 'penjual-dashboard', component: PenjualDashboard },
      { path: 'toko', name: 'penjual-toko', component: TokoSaya },
      { path: 'produk', name: 'penjual-produk', component: ProdukSaya },
      { path: 'produk/baru', name: 'penjual-produk-baru', component: ProdukForm },
      { path: 'produk/:id/edit', name: 'penjual-produk-edit', component: ProdukForm },
      { path: 'pesanan', name: 'penjual-pesanan', component: PesananMasuk }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function getRole() {
  return localStorage.getItem('role')
}

function roleHome(role) {
  if (role === 'kontributor') return { name: 'kontributor-dashboard' }
  if (role === 'penjual') return { name: 'penjual-dashboard' }
  return { name: 'admin-dashboard' }
}

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const allowedRoles = to.matched.flatMap((record) => record.meta.roles || [])
  const role = getRole()

  if (requiresAuth && !token) {
    return { name: 'login' }
  }

  if (requiresAuth && allowedRoles.length && !allowedRoles.includes(role)) {
    return roleHome(role)
  }

  if (to.name === 'login' && token) {
    return roleHome(role)
  }
})

export default router
