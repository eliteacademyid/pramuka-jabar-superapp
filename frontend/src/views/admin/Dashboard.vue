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

    <div class="card-grid" v-if="user?.role === 'admin'">
      <div v-for="stat in stats" :key="stat.label" class="stat-card">
        <span class="stat-value">{{ stat.value }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </div>
    
    <div class="card-grid" v-else-if="user?.role === 'staff'">
      <div class="stat-card">
        <h3 style="color: var(--brown); margin-bottom: 0.5rem;">Pusat Pelatihan</h3>
        <p style="font-size: 0.9rem; color: #8a7a6d; margin-bottom: 1rem;">Ikuti berbagai pelatihan untuk meningkatkan kompetensi kepramukaan Anda.</p>
        <router-link to="/admin/trainings" class="btn-primary" style="text-align: center; font-size: 0.9rem; padding: 0.5rem;">Lihat Pelatihan</router-link>
      </div>
    </div>
  </div>
</template>
