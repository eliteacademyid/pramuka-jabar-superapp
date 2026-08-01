<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import AnggotaForm from './AnggotaForm.vue'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')

const kwarcabs = ref([])
const kwarans = ref([])
const gudeps = ref([])

const items = ref([])
const total = ref(0)
const page = ref(1)
const perPage = 10

const filters = reactive({
  kwarcab_id: '',
  kwaran_id: '',
  gudep_id: '',
  golongan: '',
  status_aktif: '',
  q: ''
})

const golonganList = ['siaga', 'penggalang', 'penegak', 'pandega', 'dewasa']

const showModal = ref(false)
const isEdit = ref(false)
const editingItem = ref(null)

const filteredKwarans = () =>
  filters.kwarcab_id
    ? kwarans.value.filter((k) => k.kwarcab_id === Number(filters.kwarcab_id))
    : kwarans.value

const filteredGudeps = () =>
  filters.kwaran_id
    ? gudeps.value.filter((g) => g.kwaran_id === Number(filters.kwaran_id))
    : gudeps.value

onMounted(async () => {
  await loadOptions()
  await loadAnggota()
})

async function loadOptions() {
  try {
    const [kc, kr, g] = await Promise.all([
      api.get('/admin/kwarcab'),
      api.get('/admin/kwaran'),
      api.get('/admin/gudep')
    ])
    kwarcabs.value = kc.data
    kwarans.value = kr.data
    gudeps.value = g.data
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

async function loadAnggota() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = { page: page.value, per_page: perPage }
    if (filters.kwarcab_id) params.kwarcab_id = filters.kwarcab_id
    if (filters.kwaran_id) params.kwaran_id = filters.kwaran_id
    if (filters.gudep_id) params.gudep_id = filters.gudep_id
    if (filters.golongan) params.golongan = filters.golongan
    if (filters.status_aktif !== '') params.status_aktif = filters.status_aktif === 'true'
    if (filters.q.trim()) params.q = filters.q.trim()
    const res = await api.get('/admin/anggota', { params })
    items.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    handleError(err)
  } finally {
    loading.value = false
  }
}

function search() {
  page.value = 1
  loadAnggota()
}

function resetFilters() {
  filters.kwarcab_id = ''
  filters.kwaran_id = ''
  filters.gudep_id = ''
  filters.golongan = ''
  filters.status_aktif = ''
  filters.q = ''
  page.value = 1
  loadAnggota()
}

function totalPages() {
  return Math.max(1, Math.ceil(total.value / perPage))
}

function changePage(p) {
  if (p < 1 || p > totalPages()) return
  page.value = p
  loadAnggota()
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

async function saveAnggota(payload) {
  if (isEdit.value) {
    await api.put(`/admin/anggota/${editingItem.value.id}`, payload)
  } else {
    await api.post('/admin/anggota', payload)
  }
}

function onSaved() {
  showModal.value = false
  loadAnggota()
}

async function remove(item) {
  if (!window.confirm(`Hapus anggota "${item.nama_lengkap}"? Data akan dinonaktifkan (soft delete).`)) return
  try {
    await api.delete(`/admin/anggota/${item.id}`)
    await loadAnggota()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus anggota.')
  }
}

function golonganBadge(g) {
  return `badge badge-golongan-${g}`
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Data Anggota</h2>
        <p class="greeting">Kelola anggota tiap gudep.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Tambah Anggota</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="filter-card">
      <div class="filter-row">
        <input
          v-model="filters.q"
          type="text"
          class="search-input"
          placeholder="Cari NIS atau nama..."
          @keyup.enter="search"
        />
        <select v-model="filters.kwarcab_id" @change="filters.kwaran_id = ''; filters.gudep_id = ''">
          <option value="">Semua Kwarcab</option>
          <option v-for="k in kwarcabs" :key="k.id" :value="k.id">{{ k.nama }}</option>
        </select>
        <select v-model="filters.kwaran_id" @change="filters.gudep_id = ''">
          <option value="">Semua Kwaran</option>
          <option v-for="k in filteredKwarans()" :key="k.id" :value="k.id">{{ k.nama }}</option>
        </select>
        <select v-model="filters.gudep_id">
          <option value="">Semua Gudep</option>
          <option v-for="g in filteredGudeps()" :key="g.id" :value="g.id">
            {{ g.nomor_gudep }} - {{ g.nama_pangkalan }}
          </option>
        </select>
        <select v-model="filters.golongan">
          <option value="">Semua Golongan</option>
          <option v-for="g in golonganList" :key="g" :value="g">{{ g }}</option>
        </select>
        <select v-model="filters.status_aktif">
          <option value="">Semua Status</option>
          <option value="true">Aktif</option>
          <option value="false">Nonaktif</option>
        </select>
        <button class="btn-small" @click="search">Cari</button>
        <button class="btn-small btn-ghost" @click="resetFilters">Reset</button>
      </div>
    </div>

    <div class="table-card" v-if="!loading">
      <div class="table-header-row">
        <span>Menampilkan {{ items.length }} dari {{ total }} anggota</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>NIS</th>
            <th>Nama</th>
            <th>JK</th>
            <th>Golongan</th>
            <th>Gudep</th>
            <th>Kwaran</th>
            <th>Kwarcab</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.nis_anggota }}</td>
            <td>{{ item.nama_lengkap }}</td>
            <td>{{ item.jenis_kelamin }}</td>
            <td>
              <span :class="golonganBadge(item.golongan)">{{ item.golongan }}</span>
            </td>
            <td>{{ item.nama_gudep }}</td>
            <td>{{ item.nama_kwaran }}</td>
            <td>{{ item.nama_kwarcab }}</td>
            <td>
              <span :class="item.status_aktif ? 'status status-active' : 'status status-inactive'">
                {{ item.status_aktif ? 'Aktif' : 'Nonaktif' }}
              </span>
            </td>
            <td>
              <button class="btn-small" @click="openEdit(item)">Edit</button>
              <button class="btn-small btn-danger" @click="remove(item)">Hapus</button>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="9" class="empty-row">Belum ada data anggota.</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button class="btn-small" :disabled="page <= 1" @click="changePage(page - 1)">
          &laquo; Prev
        </button>
        <span class="page-info">Halaman {{ page }} / {{ totalPages() }}</span>
        <button
          class="btn-small"
          :disabled="page >= totalPages()"
          @click="changePage(page + 1)"
        >
          Next &raquo;
        </button>
      </div>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <AnggotaForm
        :initial="editingItem"
        :is-edit="isEdit"
        :kwarcabs="kwarcabs"
        :kwarans="kwarans"
        :gudeps="gudeps"
        :save="saveAnggota"
        @saved="onSaved"
        @cancel="showModal = false"
      />
    </div>
  </div>
</template>
