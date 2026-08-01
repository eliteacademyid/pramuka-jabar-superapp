<template>
  <div v-if="wallet" class="page-container">
    <div class="page-header">
      <h2>Wallet</h2>
      <button class="btn-primary btn-add" @click="topup">+ Top-up Rp 100.000 (mock)</button>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div class="card-grid">
      <div class="stat-card">
        <span class="stat-label">Saldo</span>
        <span class="stat-value">Rp {{ fmt(wallet.wallet.balance) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Dana Ditahan (Escrow)</span>
        <span class="stat-value">Rp {{ fmt(wallet.wallet.escrow_balance) }}</span>
      </div>
    </div>

    <h3>Mutasi</h3>
    <div v-if="!wallet.transactions.length" class="empty-row">Belum ada mutasi</div>
    <table class="data-table">
      <thead><tr><th>Waktu</th><th>Jenis</th><th>Jumlah</th><th>Saldo Setelah</th><th>Catatan</th></tr></thead>
      <tbody>
        <tr v-for="t in wallet.transactions" :key="t.id">
          <td>{{ new Date(t.created_at).toLocaleString('id-ID') }}</td>
          <td>{{ t.type }}</td>
          <td :class="Number(t.amount) < 0 ? 'status-inactive' : 'status-active'">Rp {{ fmt(t.amount) }}</td>
          <td>Rp {{ fmt(t.balance_after) }}</td>
          <td>{{ t.note || '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'

const wallet = ref(null)
const error = ref('')

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

async function load() {
  const { data } = await api.get('/wallet')
  wallet.value = data
}

async function topup() {
  try {
    await api.post('/wallet/topup', { amount: 100000 })
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

onMounted(load)
</script>
