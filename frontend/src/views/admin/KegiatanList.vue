<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import KegiatanForm from './KegiatanForm.vue'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')

const items = ref([])
const programKerja = ref([])

const filters = reactive({
  tanggal_dari: '',
  tanggal_sampai: '',
  status: '',
  program_kerja_id: '',
  q: ''
})

const statusList = ['rencana', 'berjalan', 'selesai', 'dibatalkan']

const showForm = ref(false)
const isEdit = ref(false)
const editingItem = ref(null)

const showDetail = ref(false)
const detailItem = ref(null)

onMounted(async () => {
  await loadProgramKerja()
  await loadItems()
})

async function loadProgramKerja() {
  try {
    const res = await api.get('/admin/program-kerja')
    programKerja.value = res.data
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
    if (filters.tanggal_dari) params.tanggal_mulai = filters.tanggal_dari
    if (filters.tanggal_sampai) params.tanggal_selesai = filters.tanggal_sampai
    if (filters.status) params.status = filters.status
    if (filters.program_kerja_id) params.program_kerja_id = filters.program_kerja_id
    if (filters.q.trim()) params.q = filters.q.trim()
    const res = await api.get('/admin/kegiatan', { params })
    items.value = res.data
  } catch (err) {
    handleError(err)
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.tanggal_dari = ''
  filters.tanggal_sampai = ''
  filters.status = ''
  filters.program_kerja_id = ''
  filters.q = ''
  loadItems()
}

function openCreate() {
  isEdit.value = false
  editingItem.value = null
  showForm.value = true
}

function openEdit(item) {
  isEdit.value = true
  editingItem.value = item
  showForm.value = true
}

function openDetail(item) {
  detailItem.value = item
  showDetail.value = true
}

async function saveItem(payload) {
  if (isEdit.value) {
    await api.put(`/admin/kegiatan/${editingItem.value.id}`, payload)
    return editingItem.value
  }
  const res = await api.post('/admin/kegiatan', payload)
  return res.data
}

function onSaved(created) {
  if (isEdit.value) {
    showForm.value = false
    loadItems()
    return
  }
  // create: simpan dulu, tetap buka form supaya bisa langsung upload lampiran
  editingItem.value = created
  isEdit.value = true
  loadItems()
}

async function quickStatus(item, newStatus) {
  if (item.status === newStatus) return
  let params = {}
  if (item.status === 'selesai' && newStatus === 'rencana') {
    const ok = window.confirm(
      'Kegiatan ini sudah berstatus "selesai". Ubah kembali ke "rencana"?'
    )
    if (!ok) return
    params = { force: true }
  }
  try {
    await api.patch(`/admin/kegiatan/${item.id}/status`, { status: newStatus }, { params })
    item.status = newStatus
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengubah status.')
  }
}

async function remove(item) {
  if (!window.confirm(`Hapus kegiatan "${item.judul}"?`)) return
  try {
    await api.delete(`/admin/kegiatan/${item.id}`)
    await loadItems()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus kegiatan.')
  }
}

function statusBadge(s) {
  return `badge badge-status-${s}`
}

function fmtTanggal(tgl) {
  if (!tgl) return '-'
  const parts = tgl.split('-')
  const bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  return `${Number(parts[2])} ${bulan[Number(parts[1]) - 1]} ${parts[0]}`
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Kegiatan &amp; Jadwal</h2>
        <p class="greeting">Agenda kegiatan internal Kwarda Jawa Barat.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Tambah Kegiatan</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="filter-card">
      <div class="filter-row">
        <input
          v-model="filters.q"
          type="text"
          class="search-input"
          placeholder="Cari judul kegiatan..."
          @keyup.enter="loadItems"
        />
        <label class="filter-label" for="kg-f-dari">Dari:</label>
        <input id="kg-f-dari" v-model="filters.tanggal_dari" type="date" class="date-input" />
        <label class="filter-label" for="kg-f-sampai">Sampai:</label>
        <input id="kg-f-sampai" v-model="filters.tanggal_sampai" type="date" class="date-input" />
        <select v-model="filters.status">
          <option value="">Semua Status</option>
          <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
        </select>
        <select v-model="filters.program_kerja_id">
          <option value="">Semua Program Kerja</option>
          <option v-for="p in programKerja" :key="p.id" :value="p.id">{{ p.judul }}</option>
        </select>
        <button class="btn-small" @click="loadItems">Cari</button>
        <button class="btn-small btn-ghost" @click="resetFilters">Reset</button>
      </div>
    </div>

    <div class="table-card" v-if="!loading">
      <div class="table-header-row">
        <span>Total {{ items.length }} kegiatan</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>Judul</th>
            <th>Tanggal</th>
            <th>Waktu</th>
            <th>Lokasi</th>
            <th>Penanggung Jawab</th>
            <th>Program Kerja</th>
            <th>Status</th>
            <th>Publik</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.judul }}</td>
            <td>{{ fmtTanggal(item.tanggal_mulai) }}</td>
            <td>{{ item.waktu || '-' }}</td>
            <td>{{ item.lokasi || '-' }}</td>
            <td>{{ item.penanggung_jawab || '-' }}</td>
            <td>{{ item.judul_program_kerja || '-' }}</td>
            <td>
              <select
                class="status-select"
                :value="item.status"
                @change="quickStatus(item, $event.target.value)"
              >
                <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
              </select>
            </td>
            <td>
              <span v-if="item.untuk_publik" class="badge-status approved">Publik</span>
              <span v-else class="text-muted small">Internal</span>
            </td>
            <td>
              <button class="btn-small" @click="openDetail(item)">Detail</button>
              <button class="btn-small" @click="openEdit(item)">Edit</button>
              <button class="btn-small btn-danger" @click="remove(item)">Hapus</button>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="8" class="empty-row">Belum ada kegiatan.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <KegiatanForm
        :initial="editingItem"
        :is-edit="isEdit"
        :program-kerja="programKerja"
        :save="saveItem"
        @saved="onSaved"
        @cancel="showForm = false"
      />
    </div>

    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal-card detail-card">
        <h3>{{ detailItem.judul }}</h3>
        <dl class="detail-list">
          <dt>Tanggal</dt>
          <dd>{{ fmtTanggal(detailItem.tanggal_mulai) }}</dd>
          <dt>Waktu</dt>
          <dd>{{ detailItem.waktu || '-' }}</dd>
          <dt>Lokasi</dt>
          <dd>{{ detailItem.lokasi || '-' }}</dd>
          <dt>Penanggung Jawab</dt>
          <dd>{{ detailItem.penanggung_jawab || '-' }}</dd>
          <dt>Program Kerja</dt>
          <dd>{{ detailItem.judul_program_kerja || '-' }}</dd>
          <dt>Status</dt>
          <dd>
            <span :class="statusBadge(detailItem.status)">{{ detailItem.status }}</span>
          </dd>
          <dt>Deskripsi</dt>
          <dd>{{ detailItem.deskripsi || '-' }}</dd>
          <dt>Catatan Pelaksanaan</dt>
          <dd>{{ detailItem.catatan_pelaksanaan || '-' }}</dd>
          <dt>Lampiran</dt>
          <dd>
            <ul v-if="detailItem.dokumen && detailItem.dokumen.length" class="detail-docs">
              <li v-for="d in detailItem.dokumen" :key="d.id">
                <a :href="d.file_url" target="_blank" rel="noopener">{{ d.nama_file }}</a>
                ({{ d.tipe }})
              </li>
            </ul>
            <span v-else>-</span>
          </dd>
        </dl>
        <div class="modal-actions">
          <button class="btn-small" @click="showDetail = false">Tutup</button>
          <button class="btn-small" @click="openEdit(detailItem); showDetail = false">Edit</button>
        </div>
      </div>
    </div>
  </div>
</template>
