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
const statusList = ['baru', 'didisposisikan', 'selesai', 'diarsipkan']

const showKlasifikasi = ref(false)
const klsForm = ref({ kode: '', nama_klasifikasi: '' })
const klsError = ref('')
const savingKls = ref(false)

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
    const res = await api.get('/admin/surat-masuk', { params })
    items.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat surat masuk.'
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
  if (sifat === 'segera') return 'badge-sifat segera'
  if (sifat === 'rahasia') return 'badge-sifat rahasia'
  if (sifat === 'penting') return 'badge-sifat penting'
  return 'badge-sifat biasa'
}

function statusBadgeClass(status) {
  return `badge-status-sm ${status}`
}

function openDetail(item) {
  router.push({ name: 'admin-surat-masuk-detail', params: { id: item.id } })
}

function openEdit(item) {
  router.push({ name: 'admin-surat-masuk-baru', query: { edit: item.id } })
}

async function saveKlasifikasi() {
  klsError.value = ''
  if (!klsForm.value.kode.trim() || !klsForm.value.nama_klasifikasi.trim()) {
    klsError.value = 'Kode dan nama klasifikasi wajib diisi.'
    return
  }
  savingKls.value = true
  try {
    await api.post('/admin/klasifikasi-surat', klsForm.value)
    klsForm.value = { kode: '', nama_klasifikasi: '' }
    await loadKlasifikasi()
  } catch (err) {
    klsError.value = err.response?.data?.detail || 'Gagal menyimpan klasifikasi.'
  } finally {
    savingKls.value = false
  }
}

async function hapusKlasifikasi(k) {
  if (!window.confirm(`Hapus klasifikasi "${k.kode} ${k.nama_klasifikasi}"?`)) return
  try {
    await api.delete(`/admin/klasifikasi-surat/${k.id}`)
    await loadKlasifikasi()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus klasifikasi.')
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Surat Masuk</h2>
        <p class="greeting">Agenda surat masuk, disposisi, dan status penanganan.</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary btn-add" @click="showKlasifikasi = true">
          Kelola Klasifikasi
        </button>
        <router-link to="/admin/surat-masuk/baru" class="btn-primary btn-add">
          + Input Surat Masuk
        </router-link>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card">
      <div class="filters-bar">
        <input v-model="filters.q" type="text" placeholder="Cari perihal / pengirim / nomor surat..." @keyup.enter="loadItems" />
        <select v-model="filters.status" @change="loadItems">
          <option value="">Semua Status</option>
          <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
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
            <th>No. Agenda</th>
            <th>Tanggal Diterima</th>
            <th>Pengirim</th>
            <th>Perihal</th>
            <th>Sifat</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.nomor_agenda }}</td>
            <td>{{ fmtTanggal(item.tanggal_diterima) }}</td>
            <td>{{ item.pengirim }}</td>
            <td>{{ item.perihal }}</td>
            <td><span :class="sifatBadgeClass(item.sifat)">{{ item.sifat }}</span></td>
            <td><span :class="statusBadgeClass(item.status)">{{ item.status }}</span></td>
            <td>
              <button class="btn-small" @click="openDetail(item)">Detail</button>
              <button class="btn-small" @click="openEdit(item)">Edit</button>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="7" class="empty-row">Belum ada surat masuk.</td>
          </tr>
        </tbody>
      </table>
      <p class="text-muted small">Total {{ total }} surat.</p>
    </div>

    <div v-if="showKlasifikasi" class="modal-overlay" @click.self="showKlasifikasi = false">
      <div class="modal-card">
        <h3>Kelola Klasifikasi Surat</h3>
        <div v-if="klsError" class="alert-error">{{ klsError }}</div>
        <div class="form-row">
          <div class="form-group">
            <label>Kode</label>
            <input v-model="klsForm.kode" type="text" placeholder="008" />
          </div>
          <div class="form-group">
            <label>Nama Klasifikasi</label>
            <input v-model="klsForm.nama_klasifikasi" type="text" placeholder="Contoh: Humas" />
          </div>
        </div>
        <button class="btn-submit" :disabled="savingKls" @click="saveKlasifikasi">Tambah</button>
        <table class="data-table" style="margin-top: 1rem">
          <thead>
            <tr><th>Kode</th><th>Nama</th><th>Aksi</th></tr>
          </thead>
          <tbody>
            <tr v-for="k in klasifikasi" :key="k.id">
              <td>{{ k.kode }}</td>
              <td>{{ k.nama_klasifikasi }}</td>
              <td><button class="btn-small btn-danger" @click="hapusKlasifikasi(k)">Hapus</button></td>
            </tr>
          </tbody>
        </table>
        <div class="modal-actions">
          <button class="btn-small" @click="showKlasifikasi = false">Tutup</button>
        </div>
      </div>
    </div>
  </div>
</template>
