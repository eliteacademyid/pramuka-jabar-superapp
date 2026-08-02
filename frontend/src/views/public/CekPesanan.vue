<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const nomor = ref(route.query.nomor || '')
const pesanan = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const statusLabels = {
  menunggu_pembayaran: 'Menunggu Pembayaran',
  menunggu_konfirmasi: 'Menunggu Konfirmasi Penjual',
  diproses: 'Sedang Diproses',
  dikirim: 'Sedang Dikirim',
  selesai: 'Selesai',
  dibatalkan: 'Dibatalkan'
}

const statusUrutan = {
  menunggu_pembayaran: 0,
  menunggu_konfirmasi: 1,
  diproses: 2,
  dikirim: 3,
  selesai: 4
}

const tahap = [
  { key: 'menunggu_pembayaran', label: 'Pesanan Dibuat' },
  { key: 'menunggu_konfirmasi', label: 'Bukti Diupload' },
  { key: 'diproses', label: 'Pembayaran Dikonfirmasi' },
  { key: 'dikirim', label: 'Dikirim' },
  { key: 'selesai', label: 'Selesai' }
]

onMounted(() => {
  nomor.value = route.query.nomor || ''
})

async function cek() {
  errorMessage.value = ''
  pesanan.value = null
  if (!nomor.value.trim()) {
    errorMessage.value = 'Nomor pesanan wajib diisi.'
    return
  }
  loading.value = true
  try {
    const res = await api.get(`/public/marketplace/pesanan/${nomor.value.trim()}`)
    pesanan.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Pesanan tidak ditemukan.'
  } finally {
    loading.value = false
  }
}

function langkahKe(key) {
  if (pesanan.value.status === 'dibatalkan') return -1
  return statusUrutan[key]
}
function langkahAktif(key) {
  if (pesanan.value.status === 'dibatalkan') return false
  return statusUrutan[pesanan.value.status] >= langkahKe(key)
}
</script>

<template>
  <div class="marketplace-page">
    <h2>Lacak Status Pesanan</h2>
    <p class="subtitle">Masukkan nomor pesanan untuk melihat status terkini.</p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <form class="track-form" @submit.prevent="cek">
      <input v-model="nomor" type="text" placeholder="contoh: ORD-202608-004" required />
      <button class="btn-primary" type="submit" :disabled="loading">
        {{ loading ? 'Mencari...' : 'Cek Status' }}
      </button>
    </form>

    <div v-if="pesanan" class="track-result">
      <div class="order-box">
        <div class="order-row"><span>Nomor Pesanan</span><strong>{{ pesanan.nomor_pesanan }}</strong></div>
        <div class="order-row">
          <span>Status</span>
          <strong :class="['status-badge', pesanan.status === 'dibatalkan' ? 'dibatalkan' : 'aktif']">
            {{ statusLabels[pesanan.status] }}
          </strong>
        </div>
        <div class="order-row"><span>Dari Toko</span><strong>{{ pesanan.nama_toko }}</strong></div>
        <div class="order-row"><span>Total</span><strong class="total-harga">Rp {{ pesanan.total_harga.toLocaleString('id-ID') }}</strong></div>
      </div>

      <div v-if="pesanan.status !== 'dibatalkan'" class="timeline">
        <div
          v-for="(t, i) in tahap"
          :key="t.key"
          class="timeline-step"
          :class="{ done: langkahAktif(t.key), current: pesanan.status === t.key }"
        >
          <div class="timeline-dot">{{ i + 1 }}</div>
          <span class="timeline-label">{{ t.label }}</span>
        </div>
      </div>
      <div v-else class="alert-error">Pesanan ini dibatalkan.</div>

      <div class="rekening-box" v-if="pesanan.status === 'menunggu_pembayaran'">
        <h3>Transfer ke Rekening Penjual</h3>
        <div class="rekening-row"><span>Bank</span><strong>{{ pesanan.rekening.nama_bank }}</strong></div>
        <div class="rekening-row"><span>Nomor Rekening</span><strong>{{ pesanan.rekening.nomor_rekening }}</strong></div>
        <div class="rekening-row"><span>Atas Nama</span><strong>{{ pesanan.rekening.nama_pemilik_rekening }}</strong></div>
        <router-link
          :to="{ name: 'marketplace-bukti', query: { nomor: pesanan.nomor_pesanan } }"
          class="btn-primary"
        >Upload Bukti Transfer</router-link>
      </div>

      <div class="order-items" v-if="pesanan.items.length">
        <h3>Rincian Produk</h3>
        <table class="data-table">
          <thead>
            <tr><th>Produk</th><th>Harga</th><th>Jumlah</th><th>Subtotal</th></tr>
          </thead>
          <tbody>
            <tr v-for="item in pesanan.items" :key="item.id">
              <td>{{ item.nama_produk_saat_beli }}</td>
              <td>Rp {{ item.harga_saat_beli.toLocaleString('id-ID') }}</td>
              <td>{{ item.jumlah }}</td>
              <td>Rp {{ item.subtotal.toLocaleString('id-ID') }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="order-box" v-if="pesanan.bukti_transfer_url">
        <div class="order-row">
          <span>Bukti Transfer</span>
          <a :href="pesanan.bukti_transfer_url" target="_blank" rel="noopener">Lihat bukti</a>
        </div>
      </div>
    </div>
  </div>
</template>
