<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const currentUser = ref(null)
const pendingCount = ref(0)
const disposisiMenunggu = ref(0)
const realisasiPending = ref(0)
const tokoPending = ref(0)

const comingSoon = ['Berita', 'Galeri', 'Dokumen', 'Pengaturan']

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    currentUser.value = res.data
    const hub = await api.get('/admin/hub-kegiatan')
    pendingCount.value = hub.data.filter((h) => h.status === 'pending').length
    const dispo = await api.get('/admin/disposisi/saya?status=menunggu')
    disposisiMenunggu.value = dispo.data.length
    const real = await api.get('/admin/pelaporan/realisasi-pending')
    realisasiPending.value = real.data.length
    const toko = await api.get('/admin/marketplace/toko?status=pending')
    tokoPending.value = toko.data.length
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

      <div class="sidebar-section-label">Program Kegiatan Internal</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/program-kerja" class="sidebar-link">
          Program Kerja
        </router-link>
        <router-link to="/admin/kegiatan" class="sidebar-link">
          Kegiatan &amp; Jadwal
        </router-link>
        <router-link to="/admin/kalender" class="sidebar-link">
          Kalender Kegiatan
        </router-link>
      </nav>

      <div class="sidebar-section-label">Hub Kegiatan</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/hub-moderasi" class="sidebar-link">
          Moderasi Postingan
          <span v-if="pendingCount > 0" class="badge-pending">{{ pendingCount }}</span>
        </router-link>
        <router-link to="/admin/hub-rekap" class="sidebar-link">
          Rekap Kontribusi
        </router-link>
      </nav>

      <div class="sidebar-section-label">Sistem Persuratan</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/surat-masuk" class="sidebar-link">
          Surat Masuk
        </router-link>
        <router-link to="/admin/surat-keluar" class="sidebar-link">
          Surat Keluar
        </router-link>
        <router-link to="/admin/disposisi-saya" class="sidebar-link">
          Disposisi Saya
          <span v-if="disposisiMenunggu > 0" class="badge-pending">{{ disposisiMenunggu }}</span>
        </router-link>
        <router-link to="/admin/persuratan-rekap" class="sidebar-link">
          Rekap Persuratan
        </router-link>
      </nav>

      <div class="sidebar-section-label">Perencanaan &amp; Pelaporan</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/dashboard-transparansi" class="sidebar-link">
          Dashboard Transparansi
        </router-link>
        <router-link to="/admin/anggaran-alokasi" class="sidebar-link">
          Alokasi Anggaran
        </router-link>
        <router-link to="/admin/realisasi-review" class="sidebar-link">
          Realisasi Anggaran
          <span v-if="realisasiPending > 0" class="badge-pending">{{ realisasiPending }}</span>
        </router-link>
        <router-link to="/admin/laporan-kegiatan" class="sidebar-link">
          Laporan Kegiatan
        </router-link>
      </nav>

      <div class="sidebar-section-label">Marketplace</div>
      <nav class="sidebar-nav">
        <router-link to="/admin/marketplace/verifikasi-toko" class="sidebar-link">
          Verifikasi Toko
          <span v-if="tokoPending > 0" class="badge-pending">{{ tokoPending }}</span>
        </router-link>
        <router-link to="/admin/marketplace/kategori" class="sidebar-link">
          Kategori Produk
        </router-link>
        <router-link to="/admin/marketplace/rekap" class="sidebar-link">
          Rekap Marketplace
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
