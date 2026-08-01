<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Katalog Produk</h2>
      <router-link class="btn-primary btn-add" to="/account/cart">Keranjang</router-link>
    </div>

    <div class="filters">
      <input v-model="filters.q" placeholder="Cari produk…" @keyup.enter="load(1)" />
      <select v-model="filters.category" @change="load(1)">
        <option value="">Semua kategori</option>
        <option v-for="c in categories" :key="c.id" :value="c.slug">{{ c.name }}</option>
      </select>
      <input v-model="filters.city" placeholder="Kota toko" @keyup.enter="load(1)" />
      <select v-model="filters.sort" @change="load(1)">
        <option value="newest">Terbaru</option>
        <option value="bestseller">Terlaris</option>
        <option value="cheapest">Termurah</option>
        <option value="expensive">Termahal</option>
      </select>
      <button class="btn-small" @click="load(1)">Terapkan</button>
    </div>

    <div v-if="!products.length" class="empty-row">Tidak ada produk ditemukan</div>
    <div class="product-grid">
      <ProductCard v-for="p in products" :key="p.id" :product="p" />
    </div>

    <div class="pagination">
      <button class="btn-small" :disabled="page <= 1" @click="load(page - 1)">‹ Prev</button>
      <span>Halaman {{ page }} dari {{ totalPages }}</span>
      <button class="btn-small" :disabled="page >= totalPages" @click="load(page + 1)">Next ›</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import ProductCard from '../../components/ProductCard.vue'

const products = ref([])
const categories = ref([])
const totalPages = ref(1)
const page = ref(1)
const filters = ref({ q: '', category: '', city: '', sort: 'newest' })

async function load(p) {
  page.value = p
  const params = { ...filters.value, page: p, size: 12 }
  const { data } = await api.get('/products', { params })
  products.value = data.items
  totalPages.value = Math.max(1, Math.ceil(data.total / data.size))
}

onMounted(async () => {
  load(1)
  const { data } = await api.get('/categories')
  categories.value = data
})
</script>
