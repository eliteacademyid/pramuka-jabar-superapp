<template>
  <div class="page-container">
    <div class="page-header"><h2>Pencairan Dana</h2></div>

    <div v-if="error" class="alert-error">{{ error }}</div>
    <div v-if="notice" class="alert-success">{{ notice }}</div>

    <div class="form-group" style="max-width: 400px">
      <label>Jumlah (Rp)</label>
      <input v-model.number="form.amount" type="number" min="1" required />
      <label>Bank (sintetis)</label>
      <input v-model="form.bank_name" required />
      <label>Nomor Rekening</label>
      <input v-model="form.account_number" required />
      <label>Nama Pemilik</label>
      <input v-model="form.account_name" required />
      <button class="btn-submit" style="max-width: 220px" @click="submit">Ajukan Pencairan</button>
    </div>

    <h3>Riwayat</h3>
    <div v-if="!items.length" class="empty-row">Belum ada pengajuan</div>
    <table class="data-table">
      <thead><tr><th>Tanggal</th><th>Jumlah</th><th>Bank</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="w in items" :key="w.id">
          <td>{{ new Date(w.created_at).toLocaleString('id-ID') }}</td>
          <td>Rp {{ fmt(w.amount) }}</td>
          <td>{{ w.bank_name }} {{ w.account_number }}</td>
          <td>{{ w.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'

const items = ref([])
const error = ref('')
const notice = ref('')
const form = ref({ amount: null, bank_name: '', account_number: '', account_name: '' })

function fmt(v) {
  return Number(v).toLocaleString('id-ID')
}

async function load() {
  const { data } = await api.get('/wallet/seller/withdrawals')
  items.value = data
}

async function submit() {
  error.value = ''
  try {
    await api.post('/wallet/withdrawals', form.value)
    notice.value = 'Pengajuan diterima, menunggu proses admin.'
    form.value = { amount: null, bank_name: '', account_number: '', account_name: '' }
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

onMounted(load)
</script>
