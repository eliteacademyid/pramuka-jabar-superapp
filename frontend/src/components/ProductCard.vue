<template>
  <div class="product-card">
    <router-link :to="{ name: 'product-detail', params: { slug: product.slug } }" class="pc-link">
      <div class="pc-image">
        <img v-if="product.images && product.images.length" :src="product.images[0]" :alt="product.name" />
        <span v-else class="pc-placeholder">No Image</span>
        <span v-if="product.out_of_stock" class="pc-stock-badge">Stok Habis</span>
      </div>
      <div class="pc-body">
        <div class="pc-store">{{ product.store?.name || 'Toko' }}</div>
        <h4 class="pc-name">{{ product.name }}</h4>
        <div class="pc-rating">
          <span class="pc-stars">{{ ratingStars }}</span>
          <span v-if="product.rating" class="pc-rating-num">{{ product.rating }}</span>
          <span class="pc-sold">· {{ product.sold }} terjual</span>
        </div>
        <div class="pc-price">Rp {{ formatPrice(product.price) }}</div>
      </div>
    </router-link>
    <button class="pc-btn" :disabled="product.out_of_stock || adding" @click="addToCart">
      {{ adding ? 'Menambahkan…' : added ? '✓ Ditambahkan' : '+ Tambah ke Keranjang' }}
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import api, { getErrorMessage } from '../services/api'

const props = defineProps({
  product: { type: Object, required: true }
})

const emit = defineEmits(['added', 'error'])

const adding = ref(false)
const added = ref(false)

const ratingStars = computed(() => {
  const r = Number(props.product.rating || 0)
  return '★'.repeat(Math.round(r)) + '☆'.repeat(5 - Math.round(r))
})

function formatPrice(v) {
  return Number(v).toLocaleString('id-ID')
}

async function addToCart() {
  if (!localStorage.getItem('token')) {
    window.location.href = '/login'
    return
  }
  if (adding.value) return
  adding.value = true
  try {
    await api.post('/cart/items', { product_id: props.product.id, qty: 1 })
    added.value = true
    emit('added', props.product.name)
    setTimeout(() => { added.value = false }, 1500)
  } catch (err) {
    emit('error', getErrorMessage(err))
  } finally {
    adding.value = false
  }
}
</script>
