import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../components/PublicLayout.vue'
import AccountLayout from '../components/AccountLayout.vue'
import AdminLayout from '../components/AdminLayout.vue'
import LandingPage from '../views/public/LandingPage.vue'
import LoginPage from '../views/public/LoginPage.vue'
import RegisterPage from '../views/public/RegisterPage.vue'
import CatalogPage from '../views/public/CatalogPage.vue'
import ProductDetailPage from '../views/public/ProductDetailPage.vue'
import StorePage from '../views/public/StorePage.vue'
import CartPage from '../views/account/CartPage.vue'
import CheckoutPage from '../views/account/CheckoutPage.vue'
import OrderListPage from '../views/account/OrderListPage.vue'
import OrderDetailPage from '../views/account/OrderDetailPage.vue'
import WalletPage from '../views/account/WalletPage.vue'
import ProfilePage from '../views/account/ProfilePage.vue'
import SellerStorePage from '../views/account/SellerStorePage.vue'
import SellerProductsPage from '../views/account/SellerProductsPage.vue'
import SellerProductFormPage from '../views/account/SellerProductFormPage.vue'
import SellerOrdersPage from '../views/account/SellerOrdersPage.vue'
import SellerDashboardPage from '../views/account/SellerDashboardPage.vue'
import WithdrawPage from '../views/account/WithdrawPage.vue'
import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'
import StoresPage from '../views/admin/StoresPage.vue'
import ProductsPage from '../views/admin/ProductsPage.vue'
import OrdersPage from '../views/admin/OrdersPage.vue'
import WithdrawalsPage from '../views/admin/WithdrawalsPage.vue'
import ReportsPage from '../views/admin/ReportsPage.vue'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      { path: '', name: 'landing', component: LandingPage },
      { path: 'login', name: 'login', component: LoginPage },
      { path: 'register', name: 'register', component: RegisterPage },
      { path: 'catalog', name: 'catalog', component: CatalogPage },
      { path: 'products/:slug', name: 'product-detail', component: ProductDetailPage },
      { path: 'stores/:slug', name: 'store-page', component: StorePage }
    ]
  },
  {
    path: '/account',
    component: AccountLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'cart', name: 'cart', component: CartPage },
      { path: 'checkout', name: 'checkout', component: CheckoutPage },
      { path: 'orders', name: 'orders', component: OrderListPage },
      { path: 'orders/:code', name: 'order-detail', component: OrderDetailPage },
      { path: 'wallet', name: 'wallet', component: WalletPage },
      { path: 'profile', name: 'profile', component: ProfilePage },
      { path: 'seller/store', name: 'seller-store', component: SellerStorePage },
      { path: 'seller/products', name: 'seller-products', component: SellerProductsPage },
      { path: 'seller/products/new', name: 'seller-product-new', component: SellerProductFormPage },
      { path: 'seller/products/:id', name: 'seller-product-edit', component: SellerProductFormPage },
      { path: 'seller/orders', name: 'seller-orders', component: SellerOrdersPage },
      { path: 'seller/dashboard', name: 'seller-dashboard', component: SellerDashboardPage },
      { path: 'seller/withdraw', name: 'seller-withdraw', component: WithdrawPage }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', name: 'admin-dashboard', component: Dashboard },
      { path: 'users', name: 'admin-users', component: Users },
      { path: 'stores', name: 'admin-stores', component: StoresPage },
      { path: 'products', name: 'admin-products', component: ProductsPage },
      { path: 'orders', name: 'admin-orders', component: OrdersPage },
      { path: 'withdrawals', name: 'admin-withdrawals', component: WithdrawalsPage },
      { path: 'reports', name: 'admin-reports', component: ReportsPage }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function isStaffAdmin(me) {
  return me && (me.user.role === 'admin' || me.user.role === 'staff')
}

router.beforeEach(async (to) => {
  const token = localStorage.getItem('token')
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)

  if (requiresAuth && !token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'login' && token) {
    return { name: 'admin-dashboard' }
  }

  if (requiresAuth && token) {
    let session
    try {
      session = await import('../services/session')
      const me = await session.fetchMe()
      if (requiresAdmin && !isStaffAdmin(me)) {
        return { name: 'landing' }
      }
    } catch (err) {
      console.error('GUARD_ERROR', err)
      if (session) session.clearSession()
      return { name: 'login' }
    }
  }
})

export default router
