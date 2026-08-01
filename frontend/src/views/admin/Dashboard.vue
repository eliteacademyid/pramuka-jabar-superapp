<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const user = ref(null)
const stats = ref([
  { label: 'Total User', value: '...' },
  { label: 'Total Berita', value: 0 },
  { label: 'Total Anggota', value: 0 },
  { label: 'Total Kegiatan', value: 0 }
])

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
  } catch {
    /* akan di-handle guard/logout di layout */
  }

  try {
    const usersRes = await api.get('/admin/users')
    stats.value[0].value = usersRes.data.length
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
