<template>
  <div class="dashboard-content">
    <div class="page-header"><h2>Semua Pesanan</h2></div>
    <select v-model="filter" class="filter-select" @change="load">
      <option value="">Semua status</option>
      <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
    </select>

    <div v-if="!orders.length" class="empty-row">Tidak ada pesanan</div>
    <table class="data-table">
      <thead><tr><th>Kode</th><th>Toko</th><th>Total</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="o in orders" :key="o.id">
          <td>{{ o.order_code }}</td>
          <td>{{ o.store_name }}</td>
          <td>Rp {{ Number(o.total).toLocaleString('id-ID') }}</td>
          <td>{{ o.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const orders = ref([])
const filter = ref('')
const statuses = ['pending_payment', 'paid', 'processed', 'shipped', 'delivered', 'completed', 'cancelled', 'refunded']

async function load() {
  const params = filter.value ? { status: filter.value } : {}
  const { data } = await api.get('/admin/orders', { params })
  orders.value = data
}

onMounted(load)
</script>
