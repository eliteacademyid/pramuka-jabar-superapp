import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import MainLayout from '../layouts/MainLayout.vue'
import AuthLayout from '../layouts/AuthLayout.vue'
import LoginPage from '../pages/Auth/LoginPage.vue'
import DashboardHome from '../pages/Dashboard/DashboardHome.vue'
import DashboardStatistik from '../pages/Dashboard/DashboardStatistik.vue'
import DashboardGrafik from '../pages/Dashboard/DashboardGrafik.vue'
import DashboardPerbandingan from '../pages/Dashboard/DashboardPerbandingan.vue'

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

  if (requiresAuth && !token) {
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
