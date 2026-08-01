<template>
  <div class="page-container">
    <div class="page-header"><h2>Pesanan Saya</h2></div>
    <select v-model="filter" class="filter-select" @change="load">
      <option value="">Semua status</option>
      <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
    </select>

    <div v-if="!orders.length" class="empty-row">Belum ada pesanan</div>
    <div v-for="o in orders" :key="o.id" class="order-card">
      <router-link :to="{ name: 'order-detail', params: { code: o.order_code } }" class="order-link">
        <div class="order-head">
          <strong>{{ o.order_code }}</strong>
          <OrderStatusChip :status="o.status" />
        </div>
        <div>{{ o.store_name }} · {{ new Date(o.created_at).toLocaleString('id-ID') }}</div>
        <div>Total: Rp {{ fmt(o.total) }} · {{ o.items.length }} item</div>
      </router-link>
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
  const { data } = await api.get('/orders', { params })
  orders.value = data
}

onMounted(load)
</script>
