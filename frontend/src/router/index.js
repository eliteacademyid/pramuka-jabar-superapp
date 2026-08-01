import { createRouter, createWebHistory } from 'vue-router'
<<<<<<< HEAD
import PublicLayout from '../components/PublicLayout.vue'
import AdminLayout from '../components/AdminLayout.vue'
import LandingPage from '../views/public/LandingPage.vue'
import LoginPage from '../views/public/LoginPage.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'
=======
import { useAuthStore } from '../store/auth'
import MainLayout from '../layouts/MainLayout.vue'
import LoginPage from '../pages/Auth/LoginPage.vue'
import DashboardHome from '../pages/Dashboard/DashboardHome.vue'
import DashboardStatistik from '../pages/Dashboard/DashboardStatistik.vue'
import DashboardGrafik from '../pages/Dashboard/DashboardGrafik.vue'
import DashboardPerbandingan from '../pages/Dashboard/DashboardPerbandingan.vue'
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)

const routes = [
  {
    path: '/',
<<<<<<< HEAD
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
=======
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: { public: true }
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
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

<<<<<<< HEAD
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)

  if (requiresAuth && !token) {
    return { name: 'login' }
  }

  if (to.name === 'login' && token) {
    return { name: 'admin-dashboard' }
=======
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
>>>>>>> b0b9cda (feat: initialize Vue 3 project with Vite)
  }
})

export default router
