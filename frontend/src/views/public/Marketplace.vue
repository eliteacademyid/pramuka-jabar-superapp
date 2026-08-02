<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const products = ref([])
const categories = ref([])
const selectedCategory = ref(null)
const search = ref('')
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const total = ref(0)
const hasMore = ref(false)

async function loadProducts(reset = true) {
  if (reset) {
    page.value = 1
    products.value = []
  }
  loading.value = true
  errorMessage.value = ''
  try {
    const params = { page: page.value, per_page: 12 }
    if (selectedCategory.value) params.kategori_id = selectedCategory.value
    if (search.value.trim()) params.search = search.value.trim()
    const res = await api.get('/public/marketplace/produk', { params })
    total.value = res.data.total
    const items = res.data.items
    products.value = reset ? items : [...products.value, ...items]
    hasMore.value = page.value * res.data.per_page < total.value

    const map = new Map()
    for (const p of items) {
      if (!map.has(p.kategori_id)) map.set(p.kategori_id, p.nama_kategori)
    }
    const current = new Map(categories.value.map((c) => [c.id, c.nama]))
    for (const [id, nama] of map) if (!current.has(id)) current.set(id, nama)
    categories.value = [...current.entries()].map(([id, nama]) => ({ id, nama }))
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat produk.'
  } finally {
    loading.value = false
  }
}

function pickCategory(id) {
  selectedCategory.value = id === selectedCategory.value ? null : id
  loadProducts(true)
}

function submitSearch() {
  loadProducts(true)
}

function loadMore() {
  page.value += 1
  loadProducts(false)
}

onMounted(() => loadProducts(true))
</script>

<template>
  <div class="marketplace-page">
    <div class="marketplace-hero">
      <h1>Marketplace Pramuka</h1>
      <p>Belanja produk khas Pramuka dan UMKM lokal dari anggota Pramuka Jawa Barat.</p>
    </div>

    <div class="marketplace-toolbar">
      <div class="search-box">
        <input
          v-model="search"
          type="text"
          placeholder="Cari produk..."
          @keyup.enter="submitSearch"
        />
        <button class="btn-primary" @click="submitSearch">Cari</button>
      </div>
      <div class="kategori-chips">
        <button
          class="chip"
          :class="{ active: selectedCategory === null }"
          @click="pickCategory(null)"
        >
          Semua
        </button>
        <button
          v-for="c in categories"
          :key="c.id"
          class="chip"
          :class="{ active: selectedCategory === c.id }"
          @click="pickCategory(c.id)"
        >
          {{ c.nama }}
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="product-grid" v-if="!loading">
      <router-link
        v-for="p in products"
        :key="p.id"
        :to="{ name: 'marketplace-produk', params: { id: p.id } }"
        class="product-card"
      >
        <div class="product-photo">
          <img v-if="p.foto_url" :src="p.foto_url" alt="foto produk" />
          <div v-else class="product-photo-placeholder">Foto</div>
        </div>
        <div class="product-info">
          <span class="product-toko">{{ p.nama_toko }}</span>
          <h3 class="product-nama">{{ p.nama_produk }}</h3>
          <div class="product-harga">Rp {{ p.harga.toLocaleString('id-ID') }}</div>
          <div class="product-meta">
            <span :class="p.stok > 0 ? 'badge badge-stock-ada' : 'badge badge-stock-habis'">
              {{ p.stok > 0 ? `Stok ${p.stok}` : 'Habis' }}
            </span>
          </div>
        </div>
      </router-link>
    </div>

    <div v-else-if="loading" class="greeting">Memuat produk...</div>
    <div v-else class="empty-row">Belum ada produk.</div>

    <div class="pagination-bar" v-if="hasMore">
      <button class="btn-small" @click="loadMore">Muat Lebih Banyak</button>
      <span class="pagination-info">Menampilkan {{ products.length }} dari {{ total }} produk</span>
    </div>

    <div class="marketplace-utils">
      <router-link to="/marketplace/cek" class="util-link">Lacak status pesanan</router-link>
      <router-link to="/marketplace/bukti" class="util-link">Upload bukti transfer</router-link>
    </div>
  </div>
</template>
