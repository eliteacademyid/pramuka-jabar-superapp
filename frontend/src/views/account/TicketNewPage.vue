<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Ajukan Perselisihan</h2>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <form class="form-stack" @submit.prevent="submit">
      <div class="field">
        <label>Kode Pesanan</label>
        <input v-model="form.order_code" required placeholder="ORD-XXXXXXXX" />
      </div>
      <div class="field">
        <label>Jenis Masalah</label>
        <select v-model="form.issue_type" required>
          <option value="" disabled>Pilih jenis masalah…</option>
          <option>Barang tidak sesuai</option>
          <option>Barang rusak / cacat</option>
          <option>Barang tidak datang</option>
          <option>Pembayaran bermasalah</option>
          <option>Pengiriman terlambat</option>
          <option>Lainnya</option>
        </select>
      </div>
      <div class="field">
        <label>Penjelasan</label>
        <textarea
          v-model="form.description"
          rows="5"
          minlength="10"
          maxlength="2000"
          required
          placeholder="Jelaskan kronologi perselisihan secara lengkap…"
        ></textarea>
      </div>
      <button class="btn-submit" type="submit" :disabled="submitting">
        {{ submitting ? 'Mengirim…' : 'Buka Tiket' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getErrorMessage } from '../../services/api'

const route = useRoute()
const router = useRouter()
const form = ref({ order_code: '', issue_type: '', description: '' })
const error = ref('')
const submitting = ref(false)

onMounted(() => {
  if (route.query.order) form.value.order_code = String(route.query.order)
})

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const { data } = await api.post('/tickets', form.value)
    router.push({ name: 'ticket-detail', params: { id: data.id } })
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    submitting.value = false
  }
}
</script>
