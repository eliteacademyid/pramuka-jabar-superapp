<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const produk = ref(null)
const jumlah = ref(1)
const form = ref({
  nama_pembeli: '',
  kontak_pembeli: '',
  alamat_pengiriman: '',
  catatan_pembeli: ''
})
const loading = ref(true)
const errorMessage = ref('')
const saving = ref(false)
const hasil = ref(null)

onMounted(async () => {
  jumlah.value = parseInt(route.query.jumlah || '1', 10) || 1
  try {
    const res = await api.get(`/public/marketplace/produk/${route.query.produk_id}`)
    produk.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Produk tidak ditemukan.'
  } finally {
    loading.value = false
  }
})

async function submitCheckout() {
  errorMessage.value = ''
  if (!form.value.nama_pembeli.trim()) {
    errorMessage.value = 'Nama pembeli wajib diisi.'
    return
  }
  if (!form.value.kontak_pembeli.trim()) {
    errorMessage.value = 'Kontak (WA/telepon) wajib diisi.'
    return
  }
  if (!form.value.alamat_pengiriman.trim()) {
    errorMessage.value = 'Alamat pengiriman wajib diisi.'
    return
  }
  saving.value = true
  try {
    const res = await api.post('/public/marketplace/pesanan', {
      toko_id: produk.value.toko_id,
      nama_pembeli: form.value.nama_pembeli,
      kontak_pembeli: form.value.kontak_pembeli,
      alamat_pengiriman: form.value.alamat_pengiriman,
      catatan_pembeli: form.value.catatan_pembeli || null,
      items: [{ produk_id: produk.value.id, jumlah: jumlah.value }]
    })
    hasil.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal membuat pesanan.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="marketplace-page">
    <router-link to="/marketplace" class="back-link">Kembali ke Marketplace</router-link>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="hasil" class="checkout-success">
      <h2>Pesanan Berhasil Dibuat!</h2>
      <p>Silakan transfer ke rekening penjual lalu upload bukti transfer.</p>

      <div class="order-box">
        <div class="order-row">
          <span>Nomor Pesanan</span>
          <strong>{{ hasil.nomor_pesanan }}</strong>
        </div>
        <div class="order-row">
          <span>Total yang harus dibayar</span>
          <strong class="total-harga">Rp {{ hasil.total_harga.toLocaleString('id-ID') }}</strong>
        </div>
      </div>

      <div class="rekening-box">
        <h3>Rekening Tujuan Transfer</h3>
        <div class="rekening-row"><span>Bank</span><strong>{{ hasil.rekening.nama_bank }}</strong></div>
        <div class="rekening-row"><span>Nomor Rekening</span><strong>{{ hasil.rekening.nomor_rekening }}</strong></div>
        <div class="rekening-row"><span>Atas Nama</span><strong>{{ hasil.rekening.nama_pemilik_rekening }}</strong></div>
        <p v-if="hasil.rekening.nomor_wa" class="rekening-wa">
          Konfirmasi via WA: {{ hasil.rekening.nomor_wa }}
        </p>
      </div>

      <div class="order-actions">
        <router-link
          :to="{ name: 'marketplace-bukti', query: { nomor: hasil.nomor_pesanan } }"
          class="btn-primary"
        >Upload Bukti Transfer</router-link>
        <router-link
          :to="{ name: 'marketplace-cek', query: { nomor: hasil.nomor_pesanan } }"
          class="btn-small"
        >Cek Status Pesanan</router-link>
      </div>
    </div>

    <template v-else>
      <h2 class="checkout-title">Checkout</h2>

      <div v-if="produk" class="checkout-layout">
        <div class="checkout-summary">
          <div class="checkout-item">
            <div class="checkout-item-photo">
              <img v-if="produk.foto_url" :src="produk.foto_url" alt="" />
              <div v-else class="product-photo-placeholder">Foto</div>
            </div>
            <div>
              <strong>{{ produk.nama_produk }}</strong>
              <span>{{ produk.nama_toko }}</span>
              <span>Rp {{ produk.harga.toLocaleString('id-ID') }} x {{ jumlah }}</span>
            </div>
            <div class="checkout-subtotal">
              Rp {{ (produk.harga * jumlah).toLocaleString('id-ID') }}
            </div>
          </div>
          <div class="checkout-total">
            <span>Total</span>
            <strong>Rp {{ (produk.harga * jumlah).toLocaleString('id-ID') }}</strong>
          </div>
          <p class="form-hint">Metode pembayaran: transfer manual ke rekening penjual (info rekening tampil setelah pesanan dibuat).</p>
        </div>

        <form class="modal-card checkout-form" @submit.prevent="submitCheckout">
          <div class="form-group">
            <label>Nama Pembeli</label>
            <input v-model="form.nama_pembeli" type="text" placeholder="Nama lengkap" required />
          </div>
          <div class="form-group">
            <label>Kontak (WA/Telepon)</label>
            <input v-model="form.kontak_pembeli" type="text" placeholder="08xx..." required />
          </div>
          <div class="form-group">
            <label>Alamat Pengiriman</label>
            <textarea v-model="form.alamat_pengiriman" rows="3" placeholder="Alamat lengkap" required></textarea>
          </div>
          <div class="form-group">
            <label>Catatan (opsional)</label>
            <input v-model="form.catatan_pembeli" type="text" placeholder="Catatan untuk penjual" />
          </div>
          <button class="btn-submit" type="submit" :disabled="saving">
            {{ saving ? 'Memproses...' : 'Buat Pesanan' }}
          </button>
        </form>
      </div>
      <div v-else-if="loading" class="greeting">Memuat produk...</div>
    </template>
  </div>
</template>
