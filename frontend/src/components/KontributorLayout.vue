<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const currentUser = ref(null)

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    currentUser.value = res.data
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
  <div class="kontributor-layout">
    <header class="kontributor-header">
      <div class="kontributor-brand">Super Apps Pramuka Jabar</div>
      <nav class="kontributor-nav">
        <router-link to="/kontributor" class="kontributor-link">Beranda</router-link>
        <router-link to="/kontributor/saya" class="kontributor-link">Postingan Saya</router-link>
        <router-link to="/kontributor/tulis" class="kontributor-link kontributor-cta">+ Buat Postingan</router-link>
      </nav>
      <div class="kontributor-user">
        <span class="kontributor-role">Kontributor</span>
        <button class="btn-logout" @click="logout">Logout</button>
      </div>
    </header>

    <main class="kontributor-main">
      <router-view />
    </main>
  </div>
</template>
