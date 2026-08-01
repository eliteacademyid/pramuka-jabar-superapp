<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const currentUser = ref(null)

const comingSoon = ['Berita', 'Kegiatan', 'Galeri', 'Dokumen', 'Pengaturan']

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
  router.push({ name: 'landing' })
}
</script>

<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo"></div>
        <div class="sidebar-title">Super Apps<br />Pramuka Jabar</div>
      </div>

      <nav class="sidebar-nav">
        <router-link to="/admin" class="sidebar-link">
          Dashboard
        </router-link>
        <router-link to="/admin/users" class="sidebar-link">
          Manajemen User
        </router-link>
      </nav>

      <div class="sidebar-section-label">Data Potensi Keanggotaan</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/wilayah" class="sidebar-link">
          Data Wilayah
        </router-link>
        <router-link to="/admin/anggota" class="sidebar-link">
          Data Anggota
        </router-link>
        <router-link to="/admin/rekap" class="sidebar-link">
          Rekap Statistik
        </router-link>
      </nav>

      <div class="sidebar-section-label">Menu Lainnya (Segera Hadir)</div>
      <nav class="sidebar-nav">
        <span v-for="item in comingSoon" :key="item" class="sidebar-link disabled">
          {{ item }}
        </span>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-name">{{ currentUser?.nama_lengkap || 'Memuat...' }}</span>
          <span class="user-role">{{ currentUser?.role }}</span>
        </div>
        <button class="btn-logout" @click="logout">Logout</button>
      </div>
    </aside>

    <main class="sidebar-content">
      <router-view />
    </main>
  </div>
</template>
