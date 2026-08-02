<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const rekap = ref(null)
const loading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/admin/marketplace/rekap')
    rekap.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat rekap.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Rekap Marketplace</h1>
      <p>Ringkasan aktivitas marketplace (transaksi bulan berjalan).</p>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="loading" class="greeting">Memuat rekap...</div>

    <div v-else-if="rekap" class="stat-grid">
      <div class="stat-card">
        <span class="stat-value">{{ rekap.toko_aktif }}</span>
        <span class="stat-label">Toko Aktif</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ rekap.toko_pending }}</span>
        <span class="stat-label">Toko Menunggu Verifikasi</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ rekap.total_produk }}</span>
        <span class="stat-label">Total Produk</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ rekap.total_transaksi }}</span>
        <span class="stat-label">Transaksi Bulan Ini</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">Rp {{ rekap.estimasi_nilai_transaksi.toLocaleString('id-ID') }}</span>
        <span class="stat-label">Estimasi Nilai Transaksi</span>
      </div>
    </div>
  </div>
</template>
