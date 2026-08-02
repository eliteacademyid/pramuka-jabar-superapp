<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const data = ref(null)

const statusLabels = {
  pending: 'Menunggu',
  approved: 'Disetujui',
  rejected: 'Ditolak'
}
const tingkatLabels = {
  kwarcab: 'Kwarcab',
  kwaran: 'Kwaran',
  gudep: 'Gudep'
}

onMounted(loadData)

async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/hub-kegiatan/rekap')
    data.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat rekap.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">Rekap Kontribusi Hub</h1>
    <p class="page-subtitle">Ringkasan postingan dari semua kontributor per status, tingkat, dan wilayah.</p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="text-muted">Memuat...</div>

    <template v-else-if="data">
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-value">{{ data.total }}</div>
          <div class="stat-label">Total Postingan</div>
        </div>
        <div
          v-for="(count, status) in data.per_status"
          :key="status"
          class="stat-card"
        >
          <div class="stat-value">{{ count }}</div>
          <div class="stat-label">{{ statusLabels[status] }}</div>
        </div>
      </div>

      <div class="form-card">
        <h3 class="card-title">Per Tingkat Wilayah</h3>
        <div class="stat-grid">
          <div v-for="(count, tingkat) in data.per_tingkat" :key="tingkat" class="stat-card">
            <div class="stat-value">{{ count }}</div>
            <div class="stat-label">{{ tingkatLabels[tingkat] }}</div>
          </div>
        </div>
      </div>

      <div class="form-card">
        <h3 class="card-title">Per Wilayah</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Tingkat</th>
              <th>Wilayah</th>
              <th>Jumlah Postingan</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="w in data.per_wilayah" :key="`${w.tingkat_wilayah}-${w.wilayah_id}`">
              <td>{{ tingkatLabels[w.tingkat_wilayah] }}</td>
              <td>{{ w.nama_wilayah }}</td>
              <td>{{ w.jumlah }}</td>
            </tr>
            <tr v-if="!data.per_wilayah.length">
              <td colspan="3" class="text-muted">Belum ada kontribusi.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
