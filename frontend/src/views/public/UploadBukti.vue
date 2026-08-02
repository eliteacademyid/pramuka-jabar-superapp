<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const nomor = ref(route.query.nomor || '')
const file = ref(null)
const errorMessage = ref('')
const uploading = ref(false)
const hasil = ref(null)

onMounted(() => {
  nomor.value = route.query.nomor || ''
})

function onFileChange(e) {
  file.value = e.target.files[0] || null
}

async function submit() {
  errorMessage.value = ''
  if (!nomor.value.trim()) {
    errorMessage.value = 'Nomor pesanan wajib diisi.'
    return
  }
  if (!file.value) {
    errorMessage.value = 'Pilih file bukti transfer terlebih dahulu.'
    return
  }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.value)
    const res = await api.post(
      `/public/marketplace/pesanan/${nomor.value.trim()}/bukti-transfer`,
      fd
    )
    hasil.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal upload bukti transfer.'
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="marketplace-page">
    <h2>Upload Bukti Transfer</h2>
    <p class="subtitle">
      Upload bukti transfer untuk pesanan yang sudah dibayar ke rekening penjual.
    </p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="hasil" class="checkout-success">
      <h3>Bukti Berhasil Diupload</h3>
      <div class="order-box">
        <div class="order-row"><span>Nomor Pesanan</span><strong>{{ hasil.nomor_pesanan }}</strong></div>
        <div class="order-row"><span>Status</span><strong class="status-ok">{{ hasil.status }}</strong></div>
      </div>
      <p>Penjual akan mengonfirmasi pembayaran. Pantau status pesanan di halaman Lacak Pesanan.</p>
      <div class="order-actions">
        <router-link :to="{ name: 'marketplace-cek', query: { nomor: hasil.nomor_pesanan } }" class="btn-primary">
          Cek Status Pesanan
        </router-link>
      </div>
    </div>

    <form v-else class="modal-card upload-card" @submit.prevent="submit">
      <div class="form-group">
        <label>Nomor Pesanan</label>
        <input v-model="nomor" type="text" placeholder="contoh: ORD-202608-004" required />
      </div>
      <div class="form-group">
        <label>File Bukti Transfer (PDF/JPG/PNG, maks 10 MB)</label>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png" @change="onFileChange" required />
      </div>
      <button class="btn-submit" type="submit" :disabled="uploading">
        {{ uploading ? 'Mengupload...' : 'Upload Bukti' }}
      </button>
    </form>
  </div>
</template>
