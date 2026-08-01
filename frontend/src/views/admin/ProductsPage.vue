<template>
  <div class="dashboard-content">
    <div class="page-header"><h2>Moderasi Produk</h2></div>
    <select v-model="filter" class="filter-select" @change="load">
      <option value="">Semua status</option>
      <option value="draft">Draft</option>
      <option value="active">Aktif</option>
      <option value="archived">Arsip</option>
    </select>

    <div v-if="!products.length" class="empty-row">Tidak ada produk</div>
    <table class="data-table">
      <thead><tr><th>Nama</th><th>Harga</th><th>Stok</th><th>Status</th><th>Aksi</th></tr></thead>
      <tbody>
        <tr v-for="p in products" :key="p.id">
          <td>{{ p.name }}</td>
          <td>Rp {{ Number(p.price).toLocaleString('id-ID') }}</td>
          <td>{{ p.stock }}</td>
          <td>{{ p.status }}</td>
          <td>
            <button v-if="p.status !== 'archived'" class="btn-small btn-danger" @click="deactivate(p)">Nonaktifkan</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const products = ref([])
const filter = ref('')

async function load() {
  const params = filter.value ? { status: filter.value } : {}
  const { data } = await api.get('/admin/products', { params })
  products.value = data
}

async function deactivate(p) {
  await api.post(`/admin/products/${p.id}/deactivate`)
  await load()
}

onMounted(load)
</script>
