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
          Dashboard SuperApp
        </router-link>
      </nav>

      <div class="sidebar-section-label">Keanggotaan</div>
      <nav class="sidebar-nav">
        <router-link to="/keanggotaan/dashboard" class="sidebar-link">
          Dashboard Keanggotaan
        </router-link>
        <router-link to="/keanggotaan/anggota" class="sidebar-link">
          Data Anggota
        </router-link>
        <router-link to="/keanggotaan/kompetensi" class="sidebar-link">
          Pemetaan Kompetensi
        </router-link>
        <router-link to="/keanggotaan/rekap" class="sidebar-link">
          Rekapitulasi &amp; Laporan
        </router-link>
        <router-link to="/keanggotaan/administrasi" class="sidebar-link">
          Administrasi Keanggotaan
        </router-link>
        <router-link to="/keanggotaan/e-kta" class="sidebar-link">
          e-KTA Anggota
        </router-link>
      </nav>

      <div class="sidebar-section-label">Sistem</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/users" class="sidebar-link">
          Manajemen User
        </router-link>
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
