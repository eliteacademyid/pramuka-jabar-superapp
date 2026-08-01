<template>
  <div v-if="report" class="dashboard-content">
    <div class="page-header">
      <h2>Laporan ({{ report.period_days }} hari terakhir)</h2>
    </div>

    <div class="card-grid">
      <div class="stat-card">
        <span class="stat-label">User Baru</span>
        <span class="stat-value">{{ report.users }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Toko Baru</span>
        <span class="stat-value">{{ report.stores }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Produk Baru</span>
        <span class="stat-value">{{ report.products }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Volume Transaksi Selesai</span>
        <span class="stat-value">Rp {{ Number(report.transaction_volume).toLocaleString('id-ID') }}</span>
      </div>
    </div>

    <h3>Order per Status</h3>
    <div v-for="(count, status) in report.orders_by_status" :key="status" class="hint">
      {{ status }}: <strong>{{ count }}</strong>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const report = ref(null)

onMounted(async () => {
  const { data } = await api.get('/admin/reports', { params: { days: 30 } })
  report.value = data
})
</script>
