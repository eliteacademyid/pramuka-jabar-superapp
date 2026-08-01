import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
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
    name: 'login',
    component: AuthLayout,
    meta: { public: true },
    children: [
      { path: '', name: 'login', component: LoginPage }
    ]
  },
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
  {
    path: '/admin',
    component: MainLayout,
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: 'users', name: 'admin-users', component: Users }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const allowedRoles = to.matched.some((record) => record.meta.roles)
    ? to.matched.find((record) => record.meta.roles)?.meta.roles
    : null

  if (requiresAuth && !token) {
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    next({ name: 'dashboard' })
  } else if (allowedRoles && authStore.user?.role && !allowedRoles.includes(authStore.user.role)) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
