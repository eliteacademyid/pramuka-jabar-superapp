<template>
  <div class="page-container">
    <div class="page-header"><h2>Checkout</h2></div>

    <div v-if="error" class="alert-error">{{ error }}</div>
    <div v-if="success" class="alert-success">{{ success }}</div>

    <div v-if="!success">
      <div class="form-group">
        <label>Alamat Pengiriman</label>
        <select v-model="addressId" required>
          <option value="" disabled>Pilih alamat…</option>
          <option v-for="a in addresses" :key="a.id" :value="a.id">
            {{ a.label }} — {{ a.address_line }}, {{ a.city }}
          </option>
        </select>
        <router-link class="back-link" to="/account/profile">+ Kelola alamat</router-link>
      </div>

      <div v-if="cart.groups && cart.groups.length">
        <div v-for="g in cart.groups" :key="g.store_id" class="cart-group">
          <h3>{{ g.store_name }}</h3>
          <p v-for="item in g.items" :key="item.id">
            {{ item.name }} × {{ item.qty }} — Rp {{ fmt(item.subtotal) }}
          </p>
          <div class="cart-subtotal">Subtotal toko: Rp {{ fmt(g.subtotal) }}</div>
        </div>
        <div class="cart-total"><strong>Total: Rp {{ fmt(cart.total) }}</strong></div>
      </div>

      <button class="btn-submit" :disabled="loading || !addressId" style="max-width: 240px" @click="checkout">
        {{ loading ? 'Memproses…' : 'Buat Pesanan' }}
      </button>
      <p class="hint">Ongkir dihitung otomatis (mock: 10.000–25.000 per toko).</p>
    </div>

    <div v-if="success">
      <router-link class="btn-primary" :to="{ name: 'orders' }">Lihat Pesanan Saya</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'

const cart = ref({ groups: [], total: 0 })
const addresses = ref([])
const addressId = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

async function checkout() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('/cart/checkout', { address_id: Number(addressId.value) })
    success.value = 'Pesanan dibuat: ' + data.orders.join(', ') + ' — lanjutkan ke pembayaran di halaman pesanan.'
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const [c, a] = await Promise.all([api.get('/cart'), api.get('/me/addresses')])
  cart.value = c.data
  addresses.value = a.data
})
</script>
