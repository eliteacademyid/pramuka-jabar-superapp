<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const toko = ref([])
const statusFilter = ref('')
const loading = ref(true)
const errorMessage = ref('')
const acting = ref(false)

const statusLabels = { pending: 'Menunggu Verifikasi', aktif: 'Aktif', nonaktif: 'Nonaktif' }

const filterTabs = [
  { key: '', label: 'Semua' },
  { key: 'pending', label: 'Menunggu Verifikasi' },
  { key: 'aktif', label: 'Aktif' },
  { key: 'nonaktif', label: 'Nonaktif' }
]

async function muat() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const res = await api.get('/admin/marketplace/toko', { params })
    toko.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat toko.'
  } finally {
    loading.value = false
  }
}

onMounted(muat)

async function verifikasi(t, aksi) {
  const label = aksi === 'aktif' ? 'aktifkan' : 'nonaktifkan'
  if (!confirm(`Yakin ${label} toko "${t.nama_toko}"?`)) return
  acting.value = true
  try {
    await api.patch(`/admin/marketplace/toko/${t.id}/verifikasi`, { status: aksi })
    await muat()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memperbarui status toko.'
  } finally {
    acting.value = false
  }
}
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Verifikasi Toko</h1>
      <p>Setujui atau nonaktifkan toko penjual di marketplace.</p>
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

    <div v-if="loading" class="greeting">Memuat toko...</div>

    <table v-else-if="toko.length" class="data-table">
      <thead>
        <tr>
          <th>Nama Toko</th>
          <th>Pemilik</th>
          <th>Kontak</th>
          <th>Jumlah Produk</th>
          <th>Status</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in toko" :key="t.id">
          <td>
            <strong>{{ t.nama_toko }}</strong>
            <p v-if="t.deskripsi" class="cell-sub">{{ t.deskripsi }}</p>
          </td>
          <td>{{ t.nama_pemilik }}</td>
          <td>
            <p>{{ t.nama_bank }} • {{ t.nomor_rekening }}</p>
            <p v-if="t.nomor_wa" class="cell-sub">WA: {{ t.nomor_wa }}</p>
          </td>
          <td>{{ t.jumlah_produk }}</td>
          <td><span :class="['badge-pending', `toko-${t.status}`]">{{ statusLabels[t.status] }}</span></td>
          <td>
            <div class="row-actions">
              <button
                v-if="t.status === 'pending' || t.status === 'nonaktif'"
                class="btn-small"
                :disabled="acting"
                @click="verifikasi(t, 'aktif')"
              >Aktifkan</button>
              <button
                v-if="t.status === 'pending' || t.status === 'aktif'"
                class="btn-small btn-danger"
                :disabled="acting"
                @click="verifikasi(t, 'nonaktif')"
              >Nonaktifkan</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-row">Tidak ada toko pada filter ini.</div>
  </div>
</template>
