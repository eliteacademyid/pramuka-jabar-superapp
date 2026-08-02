<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const currentUser = ref(null)
const toko = ref(null)

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    currentUser.value = res.data
    try {
      const t = await api.get('/penjual/toko')
      toko.value = t.data
    } catch {
      toko.value = null
    }
  } catch {
    logout()
  }
})

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push({ name: 'landing' })
}
</script>

<template>
  <div class="penjual-layout">
    <aside class="sidebar penjual-sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo"></div>
        <div class="sidebar-title">Marketplace<br />Pramuka Jabar</div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/penjual" class="sidebar-link">Dashboard</router-link>
        <router-link to="/penjual/toko" class="sidebar-link">
          Toko Saya
          <span
            v-if="toko"
            class="badge-pending"
            :class="toko.status === 'aktif' ? 'toko-aktif' : toko.status === 'pending' ? 'toko-pending' : 'toko-nonaktif'"
          >{{ toko.status }}</span>
        </router-link>
        <router-link to="/penjual/produk" class="sidebar-link">Produk</router-link>
        <router-link to="/penjual/pesanan" class="sidebar-link">Pesanan Masuk</router-link>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-name">{{ currentUser?.nama_lengkap || 'Memuat...' }}</span>
          <span class="user-role">Penjual</span>
        </div>
        <button class="btn-logout" @click="logout">Logout</button>
      </div>
    </aside>

    <main class="sidebar-content">
      <router-view />
    </main>
  </div>
</template>
