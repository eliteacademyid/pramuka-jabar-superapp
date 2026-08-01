<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const stats = ref(null)

const golonganLabels = {
  siaga: 'Siaga',
  penggalang: 'Penggalang',
  penegak: 'Penegak',
  pandega: 'Pandega',
  dewasa: 'Dewasa'
}

const golonganColors = {
  siaga: '#e74c3c',
  penggalang: '#2ecc71',
  penegak: '#e67e22',
  pandega: '#3498db',
  dewasa: '#9b59b6'
}

onMounted(loadStats)

async function loadStats() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/anggota/statistik')
    stats.value = res.data
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
      return
    }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat statistik.'
  } finally {
    loading.value = false
  }
}

function barWidth(jumlah, total) {
  if (!total) return '0%'
  return `${Math.round((jumlah / total) * 100)}%`
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Rekap Statistik Keanggotaan</h2>
        <p class="greeting">Ringkasan potensi anggota Pramuka se-Jawa Barat.</p>
      </div>
      <button class="btn-primary btn-add" @click="loadStats">Muat Ulang</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="!loading && stats" class="stat-grid">
      <div class="stat-card">
        <div class="stat-number">{{ stats.total }}</div>
        <div class="stat-label">Total Anggota Aktif</div>
      </div>

      <div class="stat-card wide">
        <h3>Per Golongan</h3>
        <div v-for="(label, key) in golonganLabels" :key="key" class="bar-row">
          <div class="bar-label">{{ label }}</div>
          <div class="bar-track">
            <div
              class="bar-fill"
              :style="{
                width: barWidth(stats.per_golongan[key], stats.total),
                backgroundColor: golonganColors[key]
              }"
            ></div>
          </div>
          <div class="bar-value">{{ stats.per_golongan[key] }}</div>
        </div>
      </div>

      <div class="stat-card wide">
        <h3>Per Kwarcab</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Kwarcab</th>
              <th>Jumlah Anggota</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in stats.per_kwarcab" :key="row.kwarcab_id">
              <td>{{ row.nama }}</td>
              <td>{{ row.jumlah }}</td>
            </tr>
            <tr v-if="stats.per_kwarcab.length === 0">
              <td colspan="2" class="empty-row">Belum ada data.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-else-if="loading" class="greeting">Memuat data...</p>
  </div>
</template>
