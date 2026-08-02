import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../components/PublicLayout.vue'
import AdminLayout from '../components/AdminLayout.vue'
import LandingPage from '../views/public/LandingPage.vue'
import LoginPage from '../views/public/LoginPage.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'
import DashboardKeanggotaan from '../views/keanggotaan/DashboardKeanggotaan.vue'
import DataAnggota from '../views/keanggotaan/DataAnggota.vue'
import PemetaanKompetensi from '../views/keanggotaan/PemetaanKompetensi.vue'
import Rekapitulasi from '../views/keanggotaan/Rekapitulasi.vue'
import AdministrasiKeanggotaan from '../views/keanggotaan/AdministrasiKeanggotaan.vue'
import EKta from '../views/keanggotaan/EKta.vue'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      { path: '', name: 'landing', component: LandingPage },
      { path: 'login', name: 'login', component: LoginPage }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'admin-dashboard', component: Dashboard },
      { path: 'users', name: 'admin-users', component: Users }
    ]
  },
  {
    path: '/keanggotaan',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', name: 'keanggotaan-dashboard', component: DashboardKeanggotaan },
      { path: 'anggota', name: 'keanggotaan-anggota', component: DataAnggota },
      { path: 'kompetensi', name: 'keanggotaan-kompetensi', component: PemetaanKompetensi },
      { path: 'rekap', name: 'keanggotaan-rekap', component: Rekapitulasi },
      { path: 'administrasi', name: 'keanggotaan-administrasi', component: AdministrasiKeanggotaan },
      { path: 'e-kta', name: 'keanggotaan-e-kta', component: EKta }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !token) {
    return { name: 'login' }
  }

  if (to.name === 'login' && token) {
    return { name: 'keanggotaan-dashboard' }
  }
})

export default router
