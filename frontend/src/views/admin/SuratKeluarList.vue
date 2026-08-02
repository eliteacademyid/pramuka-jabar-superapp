<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const items = ref([])
const total = ref(0)

const klasifikasi = ref([])
const filters = reactive({
  status: '',
  klasifikasi_id: '',
  sifat: '',
  tanggal_dari: '',
  tanggal_sampai: '',
  q: ''
})

const sifatList = ['biasa', 'penting', 'segera', 'rahasia']
const statusList = ['draft', 'menunggu_ttd', 'terkirim']

const statusLabels = {
  draft: 'Draft',
  menunggu_ttd: 'Menunggu TTD',
  terkirim: 'Terkirim'
}

onMounted(async () => {
  await loadKlasifikasi()
  await loadItems()
})

async function loadKlasifikasi() {
  try {
    const res = await api.get('/admin/klasifikasi-surat')
    klasifikasi.value = res.data
  } catch {
    /* optional */
  }
}

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (filters.status) params.status = filters.status
    if (filters.klasifikasi_id) params.klasifikasi_id = filters.klasifikasi_id
    if (filters.sifat) params.sifat = filters.sifat
    if (filters.tanggal_dari) params.tanggal_dari = filters.tanggal_dari
    if (filters.tanggal_sampai) params.tanggal_sampai = filters.tanggal_sampai
    if (filters.q.trim()) params.q = filters.q.trim()
    const res = await api.get('/admin/surat-keluar', { params })
    items.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat surat keluar.'
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.status = ''
  filters.klasifikasi_id = ''
  filters.sifat = ''
  filters.tanggal_dari = ''
  filters.tanggal_sampai = ''
  filters.q = ''
  loadItems()
}

function fmtTanggal(iso) {
  if (!iso) return '-'
  const [y, m, d] = iso.split('-')
  const bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  return `${Number(d)} ${bulan[Number(m) - 1]} ${y}`
}

function sifatBadgeClass(sifat) {
  return `badge-sifat ${sifat}`
}

function statusBadgeClass(status) {
  return `badge-sk status-${status}`
}

function openEdit(item) {
  router.push({ name: 'admin-surat-keluar-edit', params: { id: item.id } })
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Surat Keluar</h2>
        <p class="greeting">Nomor surat digenerate otomatis saat surat dikirim ke tahap Menunggu TTD.</p>
      </div>
      <router-link to="/admin/surat-keluar/baru" class="btn-primary btn-add">
        + Buat Surat Keluar
      </router-link>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card">
      <div class="filters-bar">
        <input v-model="filters.q" type="text" placeholder="Cari perihal / tujuan / nomor surat..." @keyup.enter="loadItems" />
        <select v-model="filters.status" @change="loadItems">
          <option value="">Semua Status</option>
          <option v-for="s in statusList" :key="s" :value="s">{{ statusLabels[s] }}</option>
        </select>
        <select v-model="filters.klasifikasi_id" @change="loadItems">
          <option value="">Semua Klasifikasi</option>
          <option v-for="k in klasifikasi" :key="k.id" :value="k.id">{{ k.kode }} {{ k.nama_klasifikasi }}</option>
        </select>
        <select v-model="filters.sifat" @change="loadItems">
          <option value="">Semua Sifat</option>
          <option v-for="s in sifatList" :key="s" :value="s">{{ s }}</option>
        </select>
        <input v-model="filters.tanggal_dari" type="date" @change="loadItems" />
        <input v-model="filters.tanggal_sampai" type="date" @change="loadItems" />
        <button class="btn-outline" type="button" @click="loadItems">Cari</button>
        <button class="btn-outline" type="button" @click="resetFilters">Reset</button>
      </div>

      <div v-if="loading" class="greeting">Memuat...</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Nomor Surat</th>
            <th>Tanggal</th>
            <th>Tujuan</th>
            <th>Perihal</th>
            <th>Sifat</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.nomor_surat || 'Draft' }}</td>
            <td>{{ fmtTanggal(item.tanggal_surat) }}</td>
            <td>{{ item.tujuan }}</td>
            <td>{{ item.perihal }}</td>
            <td><span :class="sifatBadgeClass(item.sifat)">{{ item.sifat }}</span></td>
            <td><span :class="statusBadgeClass(item.status)">{{ statusLabels[item.status] }}</span></td>
            <td><button class="btn-small" @click="openEdit(item)">Buka</button></td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="7" class="empty-row">Belum ada surat keluar.</td>
          </tr>
        </tbody>
      </table>
      <p class="text-muted small">Total {{ total }} surat.</p>
    </div>
  </div>
</template>
