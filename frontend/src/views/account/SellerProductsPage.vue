<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Produk Toko</h2>
      <router-link class="btn-primary btn-add" :to="{ name: 'seller-product-new' }">+ Produk Baru</router-link>
    </div>

    <div v-if="!products.length" class="empty-row">Belum ada produk</div>
    <table class="data-table">
      <thead><tr><th>Nama</th><th>Harga</th><th>Stok</th><th>Terjual</th><th>Status</th><th>Aksi</th></tr></thead>
      <tbody>
        <tr v-for="p in products" :key="p.id">
          <td>{{ p.name }}</td>
          <td>Rp {{ fmt(p.price) }}</td>
          <td>{{ p.stock }}</td>
          <td>{{ p.sold }}</td>
          <td>{{ p.status }}</td>
          <td>
            <router-link class="btn-small" :to="{ name: 'seller-product-edit', params: { id: p.id } }">Edit</router-link>
            <button class="btn-small btn-danger" @click="remove(p)">Hapus</button>
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

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

async function load() {
  const { data } = await api.get('/seller/products')
  products.value = data
}

async function remove(p) {
  if (!confirm(`Hapus produk "${p.name}"?`)) return
  await api.delete(`/seller/products/${p.id}`)
  await load()
}

onMounted(load)
</script>
