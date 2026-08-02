import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { isTokenValid } from '../utils/auth'
import MainLayout from '../layouts/MainLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'
import LoginPage from '../pages/Auth/LoginPage.vue'
import DashboardHome from '../pages/Dashboard/DashboardHome.vue'
import DashboardStatistik from '../pages/Dashboard/DashboardStatistik.vue'
import DashboardGrafik from '../pages/Dashboard/DashboardGrafik.vue'
import DashboardPerbandingan from '../pages/Dashboard/DashboardPerbandingan.vue'
import Users from '../views/admin/Users.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: AuthLayout,
    meta: { public: true, title: 'Login' },
    children: [
      { path: '', name: 'login', component: LoginPage }
    ]
  },
  {
    path: '/dashboard',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: DashboardHome,
        meta: { title: 'Dashboard', breadcrumb: 'Dashboard' }
      },
      {
        path: 'statistik',
        name: 'dashboard-statistik',
        component: DashboardStatistik,
        meta: { title: 'Statistik', breadcrumb: 'Statistik' }
      },
      {
        path: 'grafik',
        name: 'dashboard-grafik',
        component: DashboardGrafik,
        meta: { title: 'Grafik', breadcrumb: 'Grafik' }
      },
      {
        path: 'perbandingan',
        name: 'dashboard-perbandingan',
        component: DashboardPerbandingan,
        meta: { title: 'Perbandingan', breadcrumb: 'Perbandingan' }
      }
    ]
  },
  {
    path: '/admin',
    component: MainLayout,
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      {
        path: 'users',
        name: 'admin-users',
        component: Users,
        meta: { title: 'Kelola User', breadcrumb: 'Kelola User', roles: ['admin'] }
      }
    ]
  },
  {
    path: '/programs',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'programs',
        component: () => import('../pages/Program/ProgramList.vue'),
        meta: { title: 'Daftar Program', breadcrumb: 'Daftar Program' }
      }
    ]
  },
  // Catch-all 404 redirect
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0, behavior: 'smooth' }
  }
})

// ── Navigation guard ──────────────────────────────────────────────────────

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  const isPublic = to.matched.some((r) => r.meta.public)

  // Collect required roles from matched records
  const allowedRoles = to.matched
    .map((r) => r.meta.roles)
    .filter(Boolean)
    .flat()

  // Update page title
  const pageTitle = to.meta.title ? `${to.meta.title} — Pramuka Jabar SuperApp` : 'Pramuka Jabar SuperApp'
  document.title = pageTitle

  // Not authenticated → redirect to login
  if (requiresAuth && !isTokenValid(token)) {
    return next({ name: 'login' })
  }

  // Already logged in → skip login page
  if (isPublic && isTokenValid(token)) {
    return next({ name: 'dashboard' })
  }

  // Role-based permission check
  if (allowedRoles.length > 0 && authStore.user?.role && !allowedRoles.includes(authStore.user.role)) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
