<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo"></div>
        <div class="sidebar-title">LomaScout</div>
      </div>

      <nav class="sidebar-nav">
        <div class="sidebar-section-label">Belanja</div>
        <router-link class="sidebar-link" to="/catalog">Katalog</router-link>
        <router-link class="sidebar-link" to="/account/cart">Keranjang</router-link>
        <router-link class="sidebar-link" to="/account/orders">Pesanan Saya</router-link>
        <router-link class="sidebar-link" to="/account/chat">Chat</router-link>
        <router-link class="sidebar-link" to="/account/wallet">Wallet</router-link>
        <router-link class="sidebar-link" to="/account/profile">Profil & Alamat</router-link>

        <template v-if="me && hasActiveStore(me)">
          <div class="sidebar-section-label">Toko Saya</div>
          <router-link class="sidebar-link" to="/account/seller/store">Toko</router-link>
          <router-link class="sidebar-link" to="/account/seller/dashboard">Dashboard Penjual</router-link>
          <router-link class="sidebar-link" to="/account/seller/products">Produk</router-link>
          <router-link class="sidebar-link" to="/account/seller/orders">Pesanan Masuk</router-link>
          <router-link class="sidebar-link" to="/account/seller/withdraw">Pencairan Dana</router-link>
        </template>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-name">{{ me?.user?.nama_lengkap }}</span>
          <span class="user-role">{{ me?.user?.role }}</span>
        </div>
        <button class="btn-logout" @click="logout">Keluar</button>
      </div>
    </aside>

    <main class="sidebar-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchMe, clearSession, hasActiveStore } from '../services/session'

const router = useRouter()
const me = ref(null)

onMounted(async () => {
  me.value = await fetchMe()
})

function logout() {
  clearSession()
  router.push({ name: 'login' })
}
</script>
