<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const statusLabels = {
  menunggu_pembayaran: 'Menunggu Pembayaran',
  menunggu_konfirmasi: 'Menunggu Konfirmasi',
  diproses: 'Sedang Diproses',
  dikirim: 'Sedang Dikirim',
  selesai: 'Selesai',
  dibatalkan: 'Dibatalkan'
}

const filterTabs = [
  { key: '', label: 'Semua' },
  { key: 'menunggu_pembayaran', label: 'Menunggu Bayar' },
  { key: 'menunggu_konfirmasi', label: 'Perlu Konfirmasi' },
  { key: 'diproses', label: 'Diproses' },
  { key: 'dikirim', label: 'Dikirim' },
  { key: 'selesai', label: 'Selesai' },
  { key: 'dibatalkan', label: 'Dibatalkan' }
]

const pesanan = ref([])
const statusFilter = ref('')
const loading = ref(true)
const errorMessage = ref('')
const detail = ref(null)
const acting = ref(false)

async function muat() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const res = await api.get('/penjual/pesanan', { params })
    pesanan.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat pesanan.'
  } finally {
    loading.value = false
  }
}

onMounted(muat)

function bukaDetail(p) {
  detail.value = p
}

function tutupDetail() {
  detail.value = null
}

async function konfirmasiPembayaran(p) {
  if (!confirm(`Konfirmasi pembayaran pesanan ${p.nomor_pesanan}?`)) return
  acting.value = true
  try {
    await api.patch(`/penjual/pesanan/${p.id}/konfirmasi-pembayaran`)
    await muat()
    detail.value = null
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengonfirmasi pembayaran.'
  } finally {
    acting.value = false
  }
}

async function transisiStatus(p, tujuan) {
  const label = statusLabels[tujuan]
  if (!confirm(`Ubah pesanan ${p.nomor_pesanan} menjadi "${label}"?`)) return
  acting.value = true
  try {
    await api.patch(`/penjual/pesanan/${p.id}/status`, { status: tujuan })
    await muat()
    detail.value = null
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengubah status.'
  } finally {
    acting.value = false
  }
}
</script>

<template>
  <div class="penjual-page">
    <div class="page-header">
      <h1>Pesanan Masuk</h1>
      <p>Kelola pesanan dari pembeli marketplace.</p>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="filter-tabs">
      <button
        v-for="t in filterTabs"
        :key="t.key"
        class="filter-tab"
        :class="{ active: statusFilter === t.key }"
        @click="statusFilter = t.key; muat()"
      >{{ t.label }}</button>
    </div>

    <div v-if="loading" class="greeting">Memuat pesanan...</div>

    <table v-else-if="pesanan.length" class="data-table">
      <thead>
        <tr>
          <th>Nomor</th>
          <th>Pembeli</th>
          <th>Total</th>
          <th>Status</th>
          <th>Tanggal</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in pesanan" :key="p.id">
          <td>{{ p.nomor_pesanan }}</td>
          <td>{{ p.nama_pembeli }}</td>
          <td>Rp {{ p.total_harga.toLocaleString('id-ID') }}</td>
          <td><span class="badge-pending status-ok">{{ statusLabels[p.status] }}</span></td>
          <td>{{ new Date(p.created_at).toLocaleDateString('id-ID') }}</td>
          <td><button class="btn-small" @click="bukaDetail(p)">Detail</button></td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-row">Tidak ada pesanan pada filter ini.</div>

    <div v-if="detail" class="modal-overlay" @click.self="tutupDetail">
      <div class="modal-card order-detail">
        <div class="modal-actions">
          <h2>Detail Pesanan</h2>
          <button class="btn-cancel" @click="tutupDetail">Tutup</button>
        </div>

        <div class="order-box">
          <div class="order-row"><span>Nomor Pesanan</span><strong>{{ detail.nomor_pesanan }}</strong></div>
          <div class="order-row"><span>Status</span><strong class="status-ok">{{ statusLabels[detail.status] }}</strong></div>
          <div class="order-row"><span>Pembeli</span><strong>{{ detail.nama_pembeli }}</strong></div>
          <div class="order-row"><span>Kontak</span><strong>{{ detail.kontak_pembeli }}</strong></div>
          <div class="order-row"><span>Alamat</span><strong>{{ detail.alamat_pengiriman }}</strong></div>
          <div class="order-row" v-if="detail.catatan_pembeli"><span>Catatan</span><strong>{{ detail.catatan_pembeli }}</strong></div>
          <div class="order-row"><span>Tanggal</span><strong>{{ new Date(detail.created_at).toLocaleString('id-ID') }}</strong></div>
        </div>

        <div class="order-items">
          <table class="data-table">
            <thead>
              <tr><th>Produk</th><th>Harga</th><th>Jumlah</th><th>Subtotal</th></tr>
            </thead>
            <tbody>
              <tr v-for="item in detail.items" :key="item.id">
                <td>{{ item.nama_produk_saat_beli }}</td>
                <td>Rp {{ item.harga_saat_beli.toLocaleString('id-ID') }}</td>
                <td>{{ item.jumlah }}</td>
                <td>Rp {{ item.subtotal.toLocaleString('id-ID') }}</td>
              </tr>
            </tbody>
          </table>
          <div class="checkout-total">
            <span>Total</span>
            <strong>Rp {{ detail.total_harga.toLocaleString('id-ID') }}</strong>
          </div>
        </div>

        <div class="order-box" v-if="detail.bukti_transfer_url">
          <div class="order-row">
            <span>Bukti Transfer</span>
            <a :href="detail.bukti_transfer_url" target="_blank" rel="noopener">Lihat bukti</a>
          </div>
        </div>

        <div class="order-actions">
          <button
            v-if="detail.status === 'menunggu_konfirmasi'"
            class="btn-submit"
            :disabled="acting"
            @click="konfirmasiPembayaran(detail)"
          >Konfirmasi Pembayaran</button>
          <button
            v-if="detail.status === 'diproses'"
            class="btn-submit"
            :disabled="acting"
            @click="transisiStatus(detail, 'dikirim')"
          >Kirim Pesanan</button>
          <button
            v-if="detail.status === 'dikirim'"
            class="btn-submit"
            :disabled="acting"
            @click="transisiStatus(detail, 'selesai')"
          >Tandai Selesai</button>
          <button
            v-if="['menunggu_pembayaran', 'menunggu_konfirmasi', 'diproses'].includes(detail.status)"
            class="btn-cancel"
            :disabled="acting"
            @click="transisiStatus(detail, 'dibatalkan')"
          >Batalkan Pesanan</button>
        </div>
      </div>
    </div>
  </div>
</template>
