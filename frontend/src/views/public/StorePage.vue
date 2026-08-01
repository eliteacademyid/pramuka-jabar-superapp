<template>
  <div v-if="store" class="page-container">
    <div class="store-head">
      <h2>{{ store.name }}</h2>
      <div class="detail-rating">★ {{ store.rating || '—' }}</div>
      <p>{{ store.description }}</p>
      <p class="detail-store-meta">{{ store.city }}, {{ store.province }} · {{ store.phone || '—' }}</p>
    </div>
    <div v-if="!store.products || !store.products.length" class="empty-row">Belum ada produk</div>
    <div class="product-grid">
      <ProductCard
        v-for="p in store.products"
        :key="p.id"
        :product="{ ...p, out_of_stock: p.stock <= 0, store: { name: store.name, slug: store.slug } }"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'
import ProductCard from '../../components/ProductCard.vue'

const route = useRoute()
const store = ref(null)

onMounted(async () => {
  const { data } = await api.get(`/stores/${route.params.slug}`)
  store.value = data
})
</script>
