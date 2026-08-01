<template>
  <div class="catalog-page">
    <section class="catalog-hero">
      <div class="catalog-hero-inner">
        <span class="catalog-eyebrow">Marketplace Pramuka Jabar</span>
        <h1>Katalog Produk</h1>
        <p>Produk unggulan dari UMKM &amp; toko milik anggota Pramuka Jawa Barat</p>
      <div class="catalog-search">
        <input
          v-model="filters.q"
          placeholder="Cari produk, mis. kopi, kerajinan…"
          @keyup.enter="load(1)"
        />
        <button class="catalog-search-btn" @click="load(1)">Cari</button>
      </div>
      <router-link v-if="cartCount > 0" :to="{ name: 'cart' }" class="catalog-cart-badge">
        🛒 Keranjang ({{ cartCount }})
      </router-link>
    </div>
  </section>

    <div class="page-container">
      <div class="filters">
        <div class="filter-group">
          <label>Kategori</label>
          <select v-model="filters.category" @change="load(1)">
            <option value="">Semua kategori</option>
            <option v-for="c in categories" :key="c.id" :value="c.slug">{{ c.name }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Kota</label>
          <input v-model="filters.city" placeholder="Semua kota" @keyup.enter="load(1)" />
        </div>
        <div class="filter-group">
          <label>Urutkan</label>
          <select v-model="filters.sort" @change="load(1)">
            <option value="newest">Terbaru</option>
            <option value="bestseller">Terlaris</option>
            <option value="cheapest">Termurah</option>
            <option value="expensive">Termahal</option>
          </select>
        </div>
        <button class="btn-filter-apply" @click="load(1)">Terapkan</button>
      </div>

      <div class="catalog-meta">
        <span v-if="total">{{ total }} produk ditemukan</span>
      </div>

      <div v-if="!products.length" class="empty-row catalog-empty">
        Tidak ada produk ditemukan. Coba ubah kata kunci atau filter.
      </div>

      <div v-if="products.length" class="product-grid">
        <ProductCard
          v-for="p in products"
          :key="p.id"
          :product="p"
          @added="onAdded"
          @error="onError"
        />
      </div>

      <div v-if="products.length" class="pagination">
        <button class="btn-small" :disabled="page <= 1" @click="load(page - 1)">‹ Sebelumnya</button>
        <span class="page-info">Halaman {{ page }} dari {{ totalPages }}</span>
        <button class="btn-small" :disabled="page >= totalPages" @click="load(page + 1)">Berikutnya ›</button>
      </div>

      <div v-if="toast" class="catalog-toast">{{ toast }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const products = ref([])
const categories = ref([])
const totalPages = ref(1)
const total = ref(0)
const page = ref(1)
const filters = ref({ q: '', category: '', city: '', sort: 'newest' })
const cartCount = ref(0)
const toast = ref('')
let toastTimer = null

async function load(p) {
  page.value = p
  const params = { ...filters.value, page: p, size: 12 }
  const { data } = await api.get('/products', { params })
  products.value = data.items
  total.value = data.total
  totalPages.value = Math.max(1, Math.ceil(data.total / data.size))
}

function showToast(msg) {
  toast.value = msg
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = '' }, 2500)
}

function onAdded(name) {
  cartCount.value += 1
  showToast(`"${name}" ditambahkan ke keranjang`)
}

function onError(msg) {
  showToast(`Gagal menambahkan: ${msg}`)
}

async function loadCartCount() {
  if (!localStorage.getItem('token')) return
  try {
    const { data } = await api.get('/cart')
    cartCount.value = data.groups.reduce((n, g) => n + g.items.length, 0)
  } catch (e) {
    /* keranjang butuh login; abaikan */
  }
}

onMounted(async () => {
  load(1)
  loadCartCount()
  const { data } = await api.get('/categories')
  categories.value = data
})
</script>
