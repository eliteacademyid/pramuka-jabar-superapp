<template>
  <div class="page-container">
    <div class="page-header"><h2>Pesanan Masuk</h2></div>
    <select v-model="filter" class="filter-select" @change="load">
      <option value="">Semua status</option>
      <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
    </select>

    <div v-if="!orders.length" class="empty-row">Belum ada pesanan</div>
    <div v-for="o in orders" :key="o.id" class="order-card">
      <div class="order-head">
        <strong>{{ o.order_code }}</strong>
        <OrderStatusChip :status="o.status" />
      </div>
      <div>Pembeli #{{ o.buyer_id }} · Total Rp {{ fmt(o.total) }}</div>
      <div v-if="o.items.length">
        <span v-for="i in o.items" :key="i.id">{{ i.product_name }} ×{{ i.qty }}; </span>
      </div>
      <div class="order-actions">
        <button v-if="o.status === 'paid'" class="btn-small" @click="confirm(o)">Konfirmasi</button>
        <button v-if="['paid', 'processed'].includes(o.status)" class="btn-small" @click="ship(o)">Kirim</button>
      </div>
      <div v-if="o.status === 'shipped' && o.tracking_number" class="hint">Resi: {{ o.tracking_number }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import OrderStatusChip from '../../components/OrderStatusChip.vue'

const orders = ref([])
const filter = ref('')
const statuses = ['pending_payment', 'paid', 'processed', 'shipped', 'delivered', 'completed', 'cancelled', 'refunded']

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

async function load() {
  const params = filter.value ? { status: filter.value } : {}
  const { data } = await api.get('/seller/orders', { params })
  orders.value = data
}

async function confirm(o) {
  await api.post(`/seller/orders/${o.id}/confirm`)
  await load()
}

async function ship(o) {
  const resi = prompt('Nomor resi (sintetis):', 'TRK-' + o.order_code.slice(4, 8))
  if (resi === null) return
  await api.post(`/seller/orders/${o.id}/ship`, { tracking_number: resi })
  await load()
}

onMounted(load)
</script>
