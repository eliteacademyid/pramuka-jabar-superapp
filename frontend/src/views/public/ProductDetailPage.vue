<template>
  <div v-if="product" class="page-container detail-page">
    <div class="detail-main">
      <div class="detail-gallery">
        <img v-if="product.images && product.images.length" :src="product.images[0]" :alt="product.name" class="detail-image" />
        <div v-else class="pc-placeholder detail-image">No Image</div>
      </div>
      <div class="detail-info">
        <router-link :to="{ name: 'store-page', params: { slug: product.store.slug } }" class="detail-store">
          {{ product.store.name }}
        </router-link>
        <h1>{{ product.name }}</h1>
        <div class="detail-rating">★ {{ product.rating || '—' }} · {{ product.sold }} terjual</div>
        <div class="detail-price">Rp {{ formatPrice(product.price) }}</div>
        <div class="detail-stock" :class="{ danger: product.out_of_stock }">
          {{ product.out_of_stock ? 'Stok habis' : 'Stok: ' + product.stock + ' ' + (product.unit || '') }}
        </div>
        <p class="detail-desc">{{ product.description }}</p>
        <button class="btn-submit" :disabled="product.out_of_stock" style="max-width: 240px" @click="addToCart">
          + Tambah ke Keranjang
        </button>
      </div>
    </div>

    <div class="reviews">
      <h3>
        Ulasan ({{ product.reviews?.length || 0 }})
        <span v-if="avgRating" class="review-avg">
          <StarRating :model-value="Math.round(avgRating)" readonly />
          {{ avgRating.toFixed(1) }}
        </span>
      </h3>
      <div v-if="!product.reviews || !product.reviews.length" class="empty-row">Belum ada ulasan</div>
      <div v-for="r in product.reviews" :key="r.id" class="review-item">
        <div class="review-head">
          <strong>{{ r.username }}</strong>
          <StarRating :model-value="r.rating" readonly />
        </div>
        <p>{{ r.comment || '—' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api, { getErrorMessage } from '../../services/api'
import StarRating from '../../components/StarRating.vue'

const route = useRoute()
const product = ref(null)

const avgRating = computed(() => {
  if (!product.value?.reviews?.length) return 0
  const sum = product.value.reviews.reduce((n, r) => n + r.rating, 0)
  return sum / product.value.reviews.length
})

function formatPrice(v) {
  return Number(v).toLocaleString('id-ID')
}

async function addToCart() {
  if (!localStorage.getItem('token')) {
    window.location.href = '/login'
    return
  }
  try {
    await api.post('/cart/items', { product_id: product.value.id, qty: 1 })
    alert('Ditambahkan ke keranjang')
  } catch (err) {
    alert(getErrorMessage(err))
  }
}

onMounted(async () => {
  const { data } = await api.get(`/products/${route.params.slug}`)
  product.value = data
})
</script>
