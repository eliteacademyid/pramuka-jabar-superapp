<template>
  <div v-if="data" class="page-container">
    <div class="page-header"><h2>Dashboard Penjual</h2></div>
    <div class="card-grid">
      <div class="stat-card">
        <span class="stat-label">Produk Aktif</span>
        <span class="stat-value">{{ data.active_products }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Total Penjualan (selesai)</span>
        <span class="stat-value">Rp {{ fmt(data.total_sales) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Saldo Wallet</span>
        <span class="stat-value">Rp {{ fmt(data.balance) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Dana Ditahan (Escrow)</span>
        <span class="stat-value">Rp {{ fmt(data.escrow_balance) }}</span>
      </div>
    </div>

    <h3>Pesanan per Status</h3>
    <div v-if="!Object.keys(data.orders_by_status).length" class="empty-row">Belum ada pesanan</div>
    <div v-for="(count, status) in data.orders_by_status" :key="status" class="hint">
      {{ status }}: <strong>{{ count }}</strong>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const data = ref(null)

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

onMounted(async () => {
  const { data: d } = await api.get('/seller/dashboard')
  data.value = d
})
</script>
