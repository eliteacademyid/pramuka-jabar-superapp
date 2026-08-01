<template>
  <div class="product-card">
    <router-link :to="{ name: 'product-detail', params: { slug: product.slug } }" class="pc-link">
      <div class="pc-image">
        <img v-if="product.images && product.images.length" :src="product.images[0]" :alt="product.name" />
        <span v-else class="pc-placeholder">No Image</span>
        <span v-if="product.out_of_stock" class="pc-stock-badge">Stok habis</span>
      </div>
      <div class="pc-body">
        <div class="pc-store">{{ product.store?.name || 'Toko' }}</div>
        <h4 class="pc-name">{{ product.name }}</h4>
        <div class="pc-rating">★ {{ product.rating ? product.rating : '—' }} · {{ product.sold }} terjual</div>
        <div class="pc-price">Rp {{ formatPrice(product.price) }}</div>
      </div>
    </router-link>
    <button class="btn-small" :disabled="product.out_of_stock" @click="addToCart">
      + Keranjang
    </button>
  </div>
</template>

<script setup>
import api from '../services/api'
import { getErrorMessage } from '../services/api'

const props = defineProps({
  product: { type: Object, required: true }
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
    await api.post('/cart/items', { product_id: props.product.id, qty: 1 })
    alert('Ditambahkan ke keranjang')
  } catch (err) {
    alert(getErrorMessage(err))
  }
}
</script>
