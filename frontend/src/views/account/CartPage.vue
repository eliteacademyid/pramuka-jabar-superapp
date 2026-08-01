<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Keranjang Belanja</h2>
      <router-link class="btn-primary btn-add" to="/catalog">Lanjut Belanja</router-link>
    </div>

    <div v-if="!cart.groups || !cart.groups.length" class="empty-row">Keranjang kosong</div>

    <div v-for="g in cart.groups" :key="g.store_id" class="cart-group">
      <h3>
        <router-link :to="{ name: 'store-page', params: { slug: g.store_slug } }">{{ g.store_name }}</router-link>
      </h3>
      <table class="data-table">
        <thead>
          <tr><th>Produk</th><th>Harga</th><th>Qty</th><th>Subtotal</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="item in g.items" :key="item.id">
            <td>{{ item.name }}</td>
            <td>Rp {{ fmt(item.price) }}</td>
            <td>
              <input type="number" min="1" :max="item.stock" :value="item.qty" style="width: 70px" @change="updateQty(item, $event)" />
            </td>
            <td>Rp {{ fmt(item.subtotal) }}</td>
            <td><button class="btn-small btn-danger" @click="removeItem(item)">Hapus</button></td>
          </tr>
        </tbody>
      </table>
      <div class="cart-subtotal">Subtotal: Rp {{ fmt(g.subtotal) }}</div>
    </div>

    <div v-if="cart.groups && cart.groups.length" class="cart-total">
      <strong>Total: Rp {{ fmt(cart.total) }}</strong>
      <router-link class="btn-primary" to="/account/checkout">Checkout</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'

const cart = ref({ groups: [], total: 0 })

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

async function load() {
  const { data } = await api.get('/cart')
  cart.value = data
}

async function updateQty(item, e) {
  try {
    await api.put(`/cart/items/${item.id}`, { qty: Number(e.target.value) })
    await load()
  } catch (err) {
    alert(getErrorMessage(err))
  }
}

async function removeItem(item) {
  await api.delete(`/cart/items/${item.id}`)
  await load()
}

onMounted(load)
</script>
