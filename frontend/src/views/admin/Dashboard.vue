<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'
import { getSuratMasuk, getSuratKeluar, getDisposisi } from '../../services/surat'

const user = ref(null)
const stats = ref([
  { label: 'Total User', value: '...', icon: '👥', color: 'stat-blue' },
  { label: 'Surat Masuk', value: '...', icon: '📥', color: 'stat-green' },
  { label: 'Surat Keluar', value: '...', icon: '📤', color: 'stat-orange' },
  { label: 'Disposisi Aktif', value: '...', icon: '📋', color: 'stat-purple' },
])

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
  } catch { /* handled by guard/logout */ }

  try {
    const usersRes = await api.get('/admin/users')
    stats.value[0].value = usersRes.data.length
  } catch { /* abaikan */ }

  try {
    const smRes = await getSuratMasuk()
    stats.value[1].value = smRes.data.length
  } catch { /* abaikan */ }

  try {
    const skRes = await getSuratKeluar()
    stats.value[2].value = skRes.data.length
  } catch { /* abaikan */ }

  try {
    const disRes = await getDisposisi()
    const aktif = disRes.data.filter(d => d.status !== 'Selesai')
    stats.value[3].value = aktif.length
  } catch { /* abaikan */ }
})
</script>

<template>
  <div class="dashboard-content">
    <h2 v-if="user">Selamat datang, {{ user.nama_lengkap }}!</h2>
    <h2 v-else>Memuat...</h2>
    <p class="greeting">Ringkasan data Super Apps Pramuka Jawa Barat.</p>

    <div class="card-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card" :class="stat.color">
        <span class="stat-icon">{{ stat.icon }}</span>
        <span class="stat-value">{{ stat.value }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </div>
  </div>
</template>
