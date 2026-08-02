<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const data = ref(null)

const disposisiLabels = {
  menunggu: 'Menunggu',
  diproses: 'Diproses',
  selesai: 'Selesai'
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/admin/persuratan/rekap')
    data.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat rekap.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Rekap Persuratan</h2>
        <p class="greeting">Ringkasan surat masuk, surat keluar, dan disposisi.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="greeting">Memuat...</div>

    <template v-else-if="data">
      <div class="stats-grid">
        <div class="stat-card" @click="router.push({ name: 'admin-surat-masuk' })">
          <p class="stat-label">Surat Masuk (Bulan Ini)</p>
          <p class="stat-value">{{ data.surat_masuk_bulan_ini }}</p>
        </div>
        <div class="stat-card" @click="router.push({ name: 'admin-surat-keluar' })">
          <p class="stat-label">Surat Keluar (Bulan Ini)</p>
          <p class="stat-value">{{ data.surat_keluar_bulan_ini }}</p>
        </div>
        <div class="stat-card" @click="router.push({ name: 'admin-surat-masuk' })">
          <p class="stat-label">Total Surat Masuk</p>
          <p class="stat-value">{{ data.total_surat_masuk }}</p>
        </div>
        <div class="stat-card" @click="router.push({ name: 'admin-surat-keluar' })">
          <p class="stat-label">Total Surat Keluar</p>
          <p class="stat-value">{{ data.total_surat_keluar }}</p>
        </div>
        <div class="stat-card" @click="router.push({ name: 'admin-surat-masuk' })">
          <p class="stat-label">Surat Segera Baru</p>
          <p class="stat-value urgent">{{ data.surat_segera_baru }}</p>
        </div>
        <div class="stat-card" @click="router.push({ name: 'admin-disposisi-saya' })">
          <p class="stat-label">Disposisi Menunggu Saya</p>
          <p class="stat-value">{{ data.disposisi_menunggu_saya }}</p>
        </div>
      </div>

      <div class="table-card">
        <h3 class="card-title">Status Disposisi</h3>
        <table class="data-table">
          <thead>
            <tr><th>Status</th><th>Jumlah</th></tr>
          </thead>
          <tbody>
            <tr v-for="(v, k) in data.disposisi" :key="k">
              <td>{{ disposisiLabels[k] || k }}</td>
              <td>{{ v }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
