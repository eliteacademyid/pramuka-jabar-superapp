<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const entries = ref([])
const loading = ref(true)
const errorMessage = ref('')

onMounted(loadCarts)

async function loadCarts() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/carts')
    entries.value = res.data
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
      return
    }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat status keranjang.'
  } finally {
    loading.value = false
  }
}

function hasItems(entry) {
  return entry.item_count > 0
}

function timeFmt(value) {
  return value ? new Date(value).toLocaleString('id-ID') : '—'
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Status Keranjang Belanja</h2>
        <p class="greeting">Pantau isi keranjang belanja setiap user.</p>
      </div>
      <button class="btn-primary btn-add" @click="loadCarts">Segarkan</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Produk di Keranjang</th>
            <th>Total Item</th>
            <th>Subtotal</th>
            <th>Terakhir Diubah</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in entries" :key="entry.user_id">
            <td>{{ entry.user_id }}</td>
            <td>
              <div>{{ entry.username }}</div>
              <small class="muted">{{ entry.nama_lengkap }}</small>
            </td>
            <td>
              <span v-if="hasItems(entry)" class="cart-items">
                <span
                  v-for="item in entry.items"
                  :key="item.product_id"
                  class="cart-item-chip"
                >
                  {{ item.qty }}× {{ item.name }}
                </span>
              </span>
              <span v-else class="muted">—</span>
            </td>
            <td>{{ entry.qty_total }}</td>
            <td>Rp {{ Number(entry.subtotal).toLocaleString('id-ID') }}</td>
            <td>{{ timeFmt(entry.updated_at) }}</td>
            <td>
              <span :class="hasItems(entry) ? 'status status-active' : 'status status-inactive'">
                {{ hasItems(entry) ? 'Berisi' : 'Kosong' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>
  </div>
</template>

<style scoped>
.cart-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cart-item-chip {
  background: #f4ece2;
  color: #5c4033;
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 12px;
  white-space: nowrap;
}

.muted {
  color: #8a8a8a;
}
</style>
