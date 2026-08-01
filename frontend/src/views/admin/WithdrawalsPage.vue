<template>
  <div class="dashboard-content">
    <div class="page-header"><h2>Proses Pencairan</h2></div>

    <div v-if="!items.length" class="empty-row">Tidak ada pengajuan</div>
    <table class="data-table">
      <thead><tr><th>Tanggal</th><th>Penjual</th><th>Jumlah</th><th>Bank</th><th>Status</th><th>Aksi</th></tr></thead>
      <tbody>
        <tr v-for="w in items" :key="w.id">
          <td>{{ new Date(w.created_at).toLocaleString('id-ID') }}</td>
          <td>{{ w.account_name }}</td>
          <td>Rp {{ Number(w.amount).toLocaleString('id-ID') }}</td>
          <td>{{ w.bank_name }} {{ w.account_number }}</td>
          <td>{{ w.status }}</td>
          <td v-if="w.status === 'pending'">
            <button class="btn-small" @click="process(w, 'approve')">Setujui</button>
            <button class="btn-small btn-danger" @click="process(w, 'reject')">Tolak</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const items = ref([])

async function load() {
  const { data } = await api.get('/admin/withdrawals')
  items.value = data
}

async function process(w, act) {
  await api.post(`/admin/withdrawals/${w.id}/${act}`)
  await load()
}

onMounted(load)
</script>
