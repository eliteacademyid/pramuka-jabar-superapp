<template>
  <div class="dashboard-content">
    <div class="page-header"><h2>Moderasi Toko</h2></div>
    <select v-model="filter" class="filter-select" @change="load">
      <option value="">Semua status</option>
      <option value="pending">Pending</option>
      <option value="active">Aktif</option>
      <option value="suspended">Suspend</option>
      <option value="rejected">Ditolak</option>
    </select>

    <div v-if="!stores.length" class="empty-row">Tidak ada toko</div>
    <table class="data-table">
      <thead><tr><th>Nama</th><th>Pemilik</th><th>Kota</th><th>Status</th><th>Aksi</th></tr></thead>
      <tbody>
        <tr v-for="s in stores" :key="s.id">
          <td>{{ s.name }}</td>
          <td>{{ s.owner_id }}</td>
          <td>{{ s.city }}</td>
          <td>{{ s.status }} <span v-if="s.reject_reason" class="hint">({{ s.reject_reason }})</span></td>
          <td>
            <template v-if="s.status === 'pending'">
              <button class="btn-small" @click="action(s, 'approve')">Setujui</button>
              <button class="btn-small btn-danger" @click="reject(s)">Tolak</button>
            </template>
            <button v-if="s.status === 'active'" class="btn-small btn-danger" @click="action(s, 'suspend')">Suspend</button>
            <button v-if="s.status === 'suspended'" class="btn-small" @click="action(s, 'activate')">Aktifkan</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import { getErrorMessage } from '../../services/api'

const stores = ref([])
const filter = ref('')

async function load() {
  const params = filter.value ? { status: filter.value } : {}
  const { data } = await api.get('/admin/stores', { params })
  stores.value = data
}

async function action(s, act) {
  try {
    await api.post(`/admin/stores/${s.id}/${act}`)
    await load()
  } catch (err) {
    alert(getErrorMessage(err))
  }
}

async function reject(s) {
  const reason = prompt('Alasan penolakan (min 5 karakter):')
  if (reason === null) return
  try {
    await api.post(`/admin/stores/${s.id}/reject`, { reason })
    await load()
  } catch (err) {
    alert(getErrorMessage(err))
  }
}

onMounted(load)
</script>
