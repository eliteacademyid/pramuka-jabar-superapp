import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../components/PublicLayout.vue'
import AdminLayout from '../components/AdminLayout.vue'
import LandingPage from '../views/public/LandingPage.vue'
import LoginPage from '../views/public/LoginPage.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'

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
    return { name: 'admin-dashboard' }
  }
})

export default router
