<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const data = ref(null)
const loading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/public/beranda')
    data.value = res.data.statistik_keanggotaan
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat statistik.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page">
    <h1 class="page-title">Data Kepramukaan</h1>
    <p class="page-subtitle">
      Statistik agregat keanggotaan dan struktur organisasi Kwarda Jawa Barat.
      Halaman ini hanya menampilkan angka rekap, bukan data individu anggota.
    </p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="text-muted">Memuat statistik...</div>

    <template v-else-if="data">
      <div class="stat-grid">
        <div class="stat-card">
          <span class="stat-value">{{ data.total_siaga }}</span>
          <span class="stat-label">Pramuka Siaga</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.total_penggalang }}</span>
          <span class="stat-label">Pramuka Penggalang</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.total_penegak }}</span>
          <span class="stat-label">Pramuka Penegak</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.total_pandega }}</span>
          <span class="stat-label">Pramuka Pandega</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.total_dewasa }}</span>
          <span class="stat-label">Pembina / Dewasa</span>
        </div>
      </div>

      <h2 class="section-title">Struktur Wilayah</h2>
      <div class="stat-grid">
        <div class="stat-card">
          <span class="stat-value">{{ data.total_kwarcab }}</span>
          <span class="stat-label">Kwartir Cabang</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.total_kwaran }}</span>
          <span class="stat-label">Kwartir Ranting</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.total_gudep }}</span>
          <span class="stat-label">Gugus Depan</span>
        </div>
      </div>

      <p class="home-footnote">
        Data rinci (nama, NIS, tanggal lahir, kontak) hanya dapat diakses oleh
        pengurus dengan peran admin melalui sistem internal.
      </p>
    </template>
  </div>
</template>
