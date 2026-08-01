<template>
  <div v-if="order" class="page-container">
    <div class="page-header">
      <h2>{{ order.order_code }}</h2>
      <OrderStatusChip :status="order.status" />
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div class="order-detail-grid">
      <div class="detail-col">
        <h3>Item</h3>
        <table class="data-table">
          <thead><tr><th>Produk</th><th>Harga</th><th>Qty</th><th>Total</th></tr></thead>
          <tbody>
            <tr v-for="i in order.items" :key="i.id">
              <td>{{ i.product_name }}</td>
              <td>Rp {{ fmt(i.unit_price) }}</td>
              <td>{{ i.qty }}</td>
              <td>Rp {{ fmt(i.total) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="cart-subtotal">Subtotal: Rp {{ fmt(order.subtotal) }} · Ongkir: Rp {{ fmt(order.shipping_fee) }}</div>
        <div class="cart-total">Total: Rp {{ fmt(order.total) }}</div>
        <div v-if="order.tracking_number" class="hint">Resi: {{ order.tracking_number }}</div>
      </div>

      <div class="detail-col">
        <h3>Alamat Kirim</h3>
        <p v-if="order.address_snapshot">
          {{ order.address_snapshot.label }} — {{ order.address_snapshot.address_line }},<br />
          {{ order.address_snapshot.city }}, {{ order.address_snapshot.province }}
        </p>
        <h3 style="margin-top: 1.5rem">Riwayat Status</h3>
        <ul class="history-list">
          <li v-for="h in order.status_history" :key="h.id">
            {{ h.status }} <span v-if="h.note">({{ h.note }})</span>
            <span class="hint">— {{ new Date(h.created_at).toLocaleString('id-ID') }}</span>
          </li>
        </ul>

        <div class="order-actions">
          <button v-if="order.status === 'pending_payment'" class="btn-submit" style="max-width: 220px" @click="pay">
            Bayar Sekarang
          </button>
          <button v-if="['pending_payment', 'paid'].includes(order.status)" class="btn-small btn-danger" @click="cancel">
            Batalkan
          </button>
          <button v-if="order.status === 'shipped'" class="btn-submit" style="max-width: 220px" @click="confirmReceipt">
            Saya Sudah Terima
          </button>
        </div>

        <div v-if="canReview" class="review-box">
          <h3>Beri Ulasan</h3>
          <div class="review-stars">
            <span>Rating:</span>
            <StarRating v-model="review.rating" />
          </div>
          <input v-model="review.comment" placeholder="Komentar (opsional)" />
          <button class="btn-small" @click="submitReview(order.items[0])">Kirim Ulasan</button>
        </div>
      </div>
    </div>

    <div v-if="conversationId" class="chat-section">
      <h3>Chat dengan Toko</h3>
      <ChatPanel :conversation-id="conversationId" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api, { getErrorMessage } from '../../services/api'
import OrderStatusChip from '../../components/OrderStatusChip.vue'
import ChatPanel from '../../components/ChatPanel.vue'
import StarRating from '../../components/StarRating.vue'

const route = useRoute()
const order = ref(null)
const error = ref('')
const conversationId = ref(null)
const review = ref({ rating: 5, comment: '' })

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

const canReview = computed(() => order.value && order.value.status === 'completed')

async function load() {
  const { data } = await api.get(`/orders/${route.params.code}`)
  order.value = data
  const convs = await api.get('/conversations')
  const conv = convs.data.find((c) => c.order_code === data.order_code)
  if (conv) conversationId.value = conv.id
}

async function pay() {
  try {
    await api.post(`/orders/${order.value.order_code}/pay`)
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function cancel() {
  try {
    await api.post(`/orders/${order.value.order_code}/cancel`)
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function confirmReceipt() {
  try {
    await api.post(`/orders/${order.value.order_code}/confirm-receipt`)
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function submitReview(item) {
  try {
    await api.post('/reviews', { order_item_id: item.id, ...review.value })
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

onMounted(load)
</script>
