<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const currentUser = ref(null)
const stats = ref({ total: 0, pending: 0, approved: 0, rejected: 0 })

const tingkatLabels = {
  kwarcab: 'Kwarcab',
  kwaran: 'Kwaran',
  gudep: 'Gugus Depan'
}

onMounted(async () => {
  try {
    const [me, hub] = await Promise.all([
      api.get('/auth/me'),
      api.get('/kontributor/hub-kegiatan/saya')
    ])
    currentUser.value = me.data
    const items = hub.data
    stats.value = {
      total: items.length,
      pending: items.filter((h) => h.status === 'pending').length,
      approved: items.filter((h) => h.status === 'approved').length,
      rejected: items.filter((h) => h.status === 'rejected').length
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="kontributor-page">
    <h1 class="page-title">Halo, {{ currentUser?.nama_lengkap || 'Kontributor' }}</h1>
    <p class="page-subtitle">
      Selamat datang di Hub Kegiatan. Kamu mewakili
      <strong v-if="currentUser">
        {{ tingkatLabels[currentUser.tingkat_wilayah] }} {{ currentUser.nama_wilayah || '' }}
      </strong>.
      Setiap postingan harus dimoderasi admin sebelum tampil di publik.
    </p>

    <div v-if="loading" class="text-muted">Memuat...</div>

    <template v-else>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">Total Postingan</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">Menunggu Moderasi</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">Disetujui</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">Ditolak</div>
        </div>
      </div>

      <div class="action-row">
        <router-link to="/kontributor/tulis" class="btn-submit">
          + Buat Postingan Baru
        </router-link>
        <router-link to="/kontributor/saya" class="btn-outline">
          Lihat Postingan Saya
        </router-link>
      </div>
    </template>
  </div>
</template>
