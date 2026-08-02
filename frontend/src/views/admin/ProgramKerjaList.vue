<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import ProgramKerjaForm from './ProgramKerjaForm.vue'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')

const items = ref([])
const bidang = ref([])

const filters = reactive({
  bidang_id: '',
  tahun: '',
  status: ''
})

const statusList = ['rencana', 'berjalan', 'selesai', 'dibatalkan']
const years = []
const yearNow = new Date().getFullYear()
for (let y = yearNow + 1; y >= yearNow - 4; y--) {
  years.push(y)
}

const showModal = ref(false)
const isEdit = ref(false)
const editingItem = ref(null)

onMounted(async () => {
  await loadBidang()
  await loadItems()
})

async function loadBidang() {
  try {
    const res = await api.get('/admin/bidang-kwarda')
    bidang.value = res.data
  } catch (err) {
    handleError(err)
  }
}

function handleError(err) {
  if (err.response?.status === 401 || err.response?.status === 403) {
    localStorage.removeItem('token')
    router.push({ name: 'login' })
    return
  }
  errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
}

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (filters.bidang_id) params.bidang_id = filters.bidang_id
    if (filters.tahun) params.tahun = filters.tahun
    if (filters.status) params.status = filters.status
    const res = await api.get('/admin/program-kerja', { params })
    items.value = res.data
  } catch (err) {
    handleError(err)
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.bidang_id = ''
  filters.tahun = ''
  filters.status = ''
  loadItems()
}

function openCreate() {
  isEdit.value = false
  editingItem.value = null
  showModal.value = true
}

function openEdit(item) {
  isEdit.value = true
  editingItem.value = item
  showModal.value = true
}

async function saveItem(payload) {
  if (isEdit.value) {
    await api.put(`/admin/program-kerja/${editingItem.value.id}`, payload)
  } else {
    await api.post('/admin/program-kerja', payload)
  }
}

function onSaved() {
  showModal.value = false
  loadItems()
}

async function remove(item) {
  if (!window.confirm(`Hapus program kerja "${item.judul}"?`)) return
  try {
    await api.delete(`/admin/program-kerja/${item.id}`)
    await loadItems()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus program kerja.')
  }
}

function statusBadge(s) {
  return `badge badge-status-${s}`
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Program Kerja Kwarda</h2>
        <p class="greeting">Program kerja internal Kwartir Daerah Jawa Barat.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Tambah Program Kerja</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="filter-card">
      <div class="filter-row">
        <label class="filter-label" for="pk-f-bidang">Bidang:</label>
        <select id="pk-f-bidang" v-model="filters.bidang_id">
          <option value="">Semua Bidang</option>
          <option v-for="b in bidang" :key="b.id" :value="b.id">{{ b.nama_bidang }}</option>
        </select>
        <label class="filter-label" for="pk-f-tahun">Tahun:</label>
        <select id="pk-f-tahun" v-model="filters.tahun">
          <option value="">Semua Tahun</option>
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
        <label class="filter-label" for="pk-f-status">Status:</label>
        <select id="pk-f-status" v-model="filters.status">
          <option value="">Semua Status</option>
          <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
        </select>
        <button class="btn-small" @click="loadItems">Cari</button>
        <button class="btn-small btn-ghost" @click="resetFilters">Reset</button>
      </div>
    </div>

    <div class="table-card" v-if="!loading">
      <div class="table-header-row">
        <span>Total {{ items.length }} program kerja</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>Judul</th>
            <th>Bidang</th>
            <th>Tahun</th>
            <th>Penanggung Jawab</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.judul }}</td>
            <td>{{ item.nama_bidang }}</td>
            <td>{{ item.tahun }}</td>
            <td>{{ item.penanggung_jawab || '-' }}</td>
            <td>
              <span :class="statusBadge(item.status)">{{ item.status }}</span>
            </td>
            <td>
              <button class="btn-small" @click="openEdit(item)">Edit</button>
              <button class="btn-small btn-danger" @click="remove(item)">Hapus</button>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="6" class="empty-row">Belum ada program kerja.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <ProgramKerjaForm
        :initial="editingItem"
        :is-edit="isEdit"
        :bidang="bidang"
        :save="saveItem"
        @saved="onSaved"
        @cancel="showModal = false"
      />
    </div>
  </div>
</template>
