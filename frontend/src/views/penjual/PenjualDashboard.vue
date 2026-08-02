<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const nama = ref(localStorage.getItem('username') || 'Penjual')
const toko = ref(null)
const dash = ref(null)
const loading = ref(true)

const statusLabel = {
  pending: 'Menunggu Verifikasi',
  aktif: 'Aktif',
  nonaktif: 'Nonaktif'
}

const badgeClass = computed(() =>
  toko.value ? `toko-${toko.value.status}` : 'toko-nonaktif'
)

onMounted(async () => {
  try {
    try {
      const resToko = await api.get('/penjual/toko')
      toko.value = resToko.data
    } catch (err) {
      if (err.response?.status === 404) toko.value = null
      else throw err
    }
    const resDash = await api.get('/penjual/dashboard')
    dash.value = resDash.data
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="penjual-page">
    <div class="page-header">
      <h1>Dashboard Penjual</h1>
      <p>Selamat datang, {{ nama }}! Kelola toko dan pesanan Anda di marketplace Pramuka.</p>
    </div>

    <div v-if="!loading && !toko" class="alert-error">
      Anda belum memiliki toko.
      <router-link to="/penjual/toko" class="btn-primary">Buka Toko Sekarang</router-link>
    </div>

    <div v-if="toko" class="toko-status-card">
      <strong>{{ toko.nama_toko }}</strong>
      <span :class="['badge-pending', badgeClass]">{{ statusLabel[toko.status] }}</span>
    </div>

    <div class="stat-grid" v-if="dash">
      <div class="stat-card">
        <span class="stat-value">{{ dash.jumlah_produk }}</span>
        <span class="stat-label">Total Produk</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ dash.pesanan_menunggu_konfirmasi }}</span>
        <span class="stat-label">Menunggu Konfirmasi</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">Rp {{ (dash.total_penjualan_bulan_ini || 0).toLocaleString('id-ID') }}</span>
        <span class="stat-label">Nilai Penjualan Bulan Ini</span>
      </div>
    </div>

    <div v-if="loading" class="greeting">Memuat dashboard...</div>
  </div>
</template>
