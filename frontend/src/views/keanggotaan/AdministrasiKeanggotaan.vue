<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const logs = ref([])

onMounted(async () => {
  try {
    const res = await api.get('/admin/log-audit')
    logs.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat log audit.'
  } finally {
    loading.value = false
  }
})

function formatTanggal(iso) {
  return new Date(iso).toLocaleString('id-ID', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Administrasi Keanggotaan</h2>
        <p class="greeting">Log audit aktivitas modul keanggotaan.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Pengguna</th>
            <th>Aksi</th>
            <th>Entitas</th>
            <th>Detail</th>
            <th>Waktu</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id">
            <td>{{ log.id }}</td>
            <td>{{ log.pengguna_id }}</td>
            <td><span class="badge badge-admin">{{ log.aksi }}</span></td>
            <td>{{ log.entitas }}</td>
            <td>{{ log.detail }}</td>
            <td>{{ formatTanggal(log.waktu) }}</td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="6" class="empty-row">Belum ada log audit.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>
  </div>
</template>
