<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const user = ref(null)
const stats = ref([
  { label: 'Total User', value: '...' },
  { label: 'Kegiatan Berlangsung', value: '...' },
  { label: 'Kegiatan Selesai', value: '...' },
  { label: 'Total Kegiatan', value: '...' }
])

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
  } catch {
    /* akan di-handle guard/logout di layout */
  }

  try {
    const [usersRes, statsRes] = await Promise.all([
      api.get('/admin/users'),
      api.get('/kegiatan/stats')
    ])
    stats.value[0].value = usersRes.data.length
    stats.value[1].value = statsRes.data.kegiatan_berlangsung
    stats.value[2].value = statsRes.data.kegiatan_selesai
    stats.value[3].value = statsRes.data.total_kegiatan
  } catch {
    /* abaikan jika gagal */
  }
})
</script>

<template>
  <div class="dashboard-content">
    <h2 v-if="user">Selamat datang, {{ user.nama_lengkap }}!</h2>
    <h2 v-else>Memuat...</h2>
    <p class="greeting">Ringkasan data Super Apps Pramuka Jawa Barat.</p>

    <div class="card-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card">
        <span class="stat-value">{{ stat.value }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </div>
  </div>
</template>
