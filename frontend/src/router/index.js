import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import MainLayout from '../layouts/MainLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'

// Auth
import LoginPage from '../pages/Auth/LoginPage.vue'

// Dashboard
import DashboardHome from '../pages/Dashboard/DashboardHome.vue'
import DashboardStatistik from '../pages/Dashboard/DashboardStatistik.vue'
import DashboardGrafik from '../pages/Dashboard/DashboardGrafik.vue'
import DashboardPerbandingan from '../pages/Dashboard/DashboardPerbandingan.vue'

// Modul 3 — E-Reporting
import RealisasiPage from '../pages/EReporting/RealisasiPage.vue'
import LaporanPage from '../pages/EReporting/LaporanPage.vue'
import ApprovalPage from '../pages/EReporting/ApprovalPage.vue'

// Admin
import Users from '../views/admin/Users.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },

  // ── Auth ─────────────────────────────────────────────────────
  {
    path: '/login',
    component: AuthLayout,
    meta: { public: true },
    children: [
      { path: '', name: 'login', component: LoginPage }
    ]
  },

  // ── Dashboard ─────────────────────────────────────────────────
  {
    path: '/dashboard',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: DashboardHome },
      { path: 'statistik', name: 'dashboard-statistik', component: DashboardStatistik },
      { path: 'grafik', name: 'dashboard-grafik', component: DashboardGrafik },
      { path: 'perbandingan', name: 'dashboard-perbandingan', component: DashboardPerbandingan }
    ]
  },

  // ── Modul 3: E-Reporting ──────────────────────────────────────
  {
    path: '/e-reporting',
    component: MainLayout,
    meta: { requiresAuth: true },
    redirect: '/e-reporting/realisasi',
    children: [
      {
        path: 'realisasi',
        name: 'ereporting-realisasi',
        component: RealisasiPage,
        meta: { title: 'Realisasi Program & Kegiatan' }
      },
      {
        path: 'laporan',
        name: 'ereporting-laporan',
        component: LaporanPage,
        meta: { title: 'Laporan Pelaksanaan' }
      },
      {
        path: 'approval',
        name: 'ereporting-approval',
        component: ApprovalPage,
        meta: { title: 'Approval Laporan' }
      }
    ]
  },

  // ── Admin ─────────────────────────────────────────────────────
  {
    path: '/admin',
    component: MainLayout,
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: 'users', name: 'admin-users', component: Users }
    ]
  },

  // ── Catch-all ─────────────────────────────────────────────────
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  const allowedRoles = to.matched.find((r) => r.meta.roles)?.meta.roles ?? null

  if (requiresAuth && !token) {
    return next({ name: 'login' })
  }
  if (to.name === 'login' && token) {
    return next({ name: 'dashboard' })
  }
  if (allowedRoles && authStore.user?.role && !allowedRoles.includes(authStore.user.role)) {
    return next({ name: 'dashboard' })
  }
  next()
})

export default router
