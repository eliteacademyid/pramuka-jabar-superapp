<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const currentUser = ref(null)
const suratMenuOpen = ref(false)

const comingSoon = ['Berita', 'Anggota', 'Kegiatan', 'Galeri', 'Dokumen', 'Pengaturan']

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

function toggleSuratMenu() {
  suratMenuOpen.value = !suratMenuOpen.value
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

        <!-- Persuratan Digital group -->
        <div class="sidebar-group">
          <button class="sidebar-group-toggle" @click="toggleSuratMenu">
            <span>Persuratan Digital</span>
            <span class="chevron" :class="{ open: suratMenuOpen }">▾</span>
          </button>
          <div v-show="suratMenuOpen" class="sidebar-submenu">
            <router-link to="/admin/surat-masuk" class="sidebar-link sidebar-sublink">
              Surat Masuk
            </router-link>
            <router-link to="/admin/surat-keluar" class="sidebar-link sidebar-sublink">
              Surat Keluar
            </router-link>
            <router-link to="/admin/disposisi" class="sidebar-link sidebar-sublink">
              Disposisi
            </router-link>
          </div>
        </div>
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
