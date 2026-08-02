<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')

const masterList = ref([])
const anggotaList = ref([])
const capaianList = ref([])

const showMasterModal = ref(false)
const isEditMaster = ref(false)
const editingMasterId = ref(null)
const masterForm = ref({ jenis: 'SKU', jenjang: 'siaga', nama_kompetensi: '', tingkat: '' })
const masterError = ref('')
const savingMaster = ref(false)

const showCapaianModal = ref(false)
const capaianForm = ref({ anggota_id: null, kompetensi_id: null, penguji_id: null })
const capaianError = ref('')
const savingCapaian = ref(false)

const jenisOptions = ['SKU', 'SKK', 'TKK']
const jenjangOptions = ['siaga', 'penggalang', 'penegak', 'pandega', 'dewasa']
const jenjangLabels = { siaga: 'Siaga', penggalang: 'Penggalang', penegak: 'Penegak', pandega: 'Pandega', dewasa: 'Dewasa' }

onMounted(loadAll)

async function loadAll() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [m, a, c] = await Promise.all([
      api.get('/kompetensi-master/'),
      api.get('/anggota/'),
      api.get('/capaian-kompetensi/')
    ])
    masterList.value = m.data
    anggotaList.value = a.data
    capaianList.value = c.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
}

function namaAnggota(id) {
  return anggotaList.value.find((a) => a.id === id)?.nama_lengkap || `Anggota #${id}`
}

function namaKompetensi(id) {
  return masterList.value.find((k) => k.id === id)?.nama_kompetensi || `Kompetensi #${id}`
}

function openCreateMaster() {
  isEditMaster.value = false
  editingMasterId.value = null
  masterForm.value = { jenis: 'SKU', jenjang: 'siaga', nama_kompetensi: '', tingkat: '' }
  masterError.value = ''
  showMasterModal.value = true
}

function openEditMaster(k) {
  isEditMaster.value = true
  editingMasterId.value = k.id
  masterForm.value = { jenis: k.jenis, jenjang: k.jenjang, nama_kompetensi: k.nama_kompetensi, tingkat: k.tingkat }
  masterError.value = ''
  showMasterModal.value = true
}

async function saveMaster() {
  masterError.value = ''
  savingMaster.value = true
  try {
    if (isEditMaster.value) {
      await api.put(`/kompetensi-master/${editingMasterId.value}`, masterForm.value)
    } else {
      await api.post('/kompetensi-master/', masterForm.value)
    }
    showMasterModal.value = false
    const m = await api.get('/kompetensi-master/')
    masterList.value = m.data
  } catch (err) {
    masterError.value = err.response?.data?.detail || 'Gagal menyimpan kompetensi.'
  } finally {
    savingMaster.value = false
  }
}

async function deleteMaster(k) {
  if (!window.confirm(`Hapus kompetensi "${k.nama_kompetensi}"?`)) return
  try {
    await api.delete(`/kompetensi-master/${k.id}`)
    const m = await api.get('/kompetensi-master/')
    masterList.value = m.data
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus kompetensi.')
  }
}

function openCreateCapaian() {
  capaianForm.value = { anggota_id: anggotaList.value[0]?.id || null, kompetensi_id: masterList.value[0]?.id || null, penguji_id: anggotaList.value[0]?.id || null }
  capaianError.value = ''
  showCapaianModal.value = true
}

async function saveCapaian() {
  capaianError.value = ''
  savingCapaian.value = true
  try {
    await api.post('/capaian-kompetensi/', capaianForm.value)
    showCapaianModal.value = false
    const c = await api.get('/capaian-kompetensi/')
    capaianList.value = c.data
  } catch (err) {
    capaianError.value = err.response?.data?.detail || 'Gagal mencatat capaian.'
  } finally {
    savingCapaian.value = false
  }
}

async function deleteCapaian(c) {
  if (!window.confirm('Hapus catatan capaian ini?')) return
  try {
    await api.delete(`/capaian-kompetensi/${c.id}`)
    const res = await api.get('/capaian-kompetensi/')
    capaianList.value = res.data
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus capaian.')
  }
}

function formatTanggal(iso) {
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Pemetaan Kompetensi</h2>
        <p class="greeting">Kelola master SKU/SKK/TKK dan catatan capaian anggota.</p>
      </div>
      <div class="btn-group">
        <button class="btn-primary btn-add" @click="openCreateMaster">+ Master Kompetensi</button>
        <button class="btn-primary btn-add btn-gold" @click="openCreateCapaian">+ Catat Capaian</button>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <h3 class="section-title">Master Kompetensi (SKU/SKK/TKK)</h3>
    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Jenis</th>
            <th>Jenjang</th>
            <th>Nama Kompetensi</th>
            <th>Tingkat</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="k in masterList" :key="k.id">
            <td>{{ k.id }}</td>
            <td><span class="badge badge-admin">{{ k.jenis }}</span></td>
            <td>{{ jenjangLabels[k.jenjang] || k.jenjang }}</td>
            <td>{{ k.nama_kompetensi }}</td>
            <td>{{ k.tingkat }}</td>
            <td>
              <button class="btn-small" @click="openEditMaster(k)">Edit</button>
              <button class="btn-small btn-danger" @click="deleteMaster(k)">Hapus</button>
            </td>
          </tr>
          <tr v-if="masterList.length === 0">
            <td colspan="6" class="empty-row">Belum ada kompetensi master.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <h3 class="section-title">Catatan Capaian Kompetensi</h3>
    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Anggota</th>
            <th>Kompetensi</th>
            <th>Tanggal Capai</th>
            <th>Penguji</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in capaianList" :key="c.id">
            <td>{{ c.id }}</td>
            <td>{{ namaAnggota(c.anggota_id) }}</td>
            <td>{{ namaKompetensi(c.kompetensi_id) }}</td>
            <td>{{ formatTanggal(c.tanggal_capai) }}</td>
            <td>{{ namaAnggota(c.penguji_id) }}</td>
            <td>
              <button class="btn-small btn-danger" @click="deleteCapaian(c)">Hapus</button>
            </td>
          </tr>
          <tr v-if="capaianList.length === 0">
            <td colspan="6" class="empty-row">Belum ada capaian kompetensi.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showMasterModal" class="modal-overlay" @click.self="showMasterModal = false">
      <form class="modal-card" @submit.prevent="saveMaster">
        <h3>{{ isEditMaster ? 'Edit Master Kompetensi' : 'Tambah Master Kompetensi' }}</h3>
        <div v-if="masterError" class="alert-error">{{ masterError }}</div>
        <div class="form-grid">
          <div class="form-group">
            <label for="mk-jenis">Jenis</label>
            <select id="mk-jenis" v-model="masterForm.jenis">
              <option v-for="j in jenisOptions" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="mk-jenjang">Jenjang</label>
            <select id="mk-jenjang" v-model="masterForm.jenjang">
              <option v-for="j in jenjangOptions" :key="j" :value="j">{{ jenjangLabels[j] }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label for="mk-nama">Nama Kompetensi</label>
          <input id="mk-nama" v-model="masterForm.nama_kompetensi" type="text" required />
        </div>
        <div class="form-group">
          <label for="mk-tingkat">Tingkat</label>
          <input id="mk-tingkat" v-model="masterForm.tingkat" type="text" required />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-small" @click="showMasterModal = false">Batal</button>
          <button type="submit" class="btn-submit modal-submit" :disabled="savingMaster">
            {{ savingMaster ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>

    <div v-if="showCapaianModal" class="modal-overlay" @click.self="showCapaianModal = false">
      <form class="modal-card" @submit.prevent="saveCapaian">
        <h3>Catat Capaian Kompetensi</h3>
        <div v-if="capaianError" class="alert-error">{{ capaianError }}</div>
        <div class="form-group">
          <label for="ck-anggota">Anggota</label>
          <select id="ck-anggota" v-model="capaianForm.anggota_id">
            <option v-for="a in anggotaList" :key="a.id" :value="a.id">{{ a.nama_lengkap }} ({{ jenjangLabels[a.jenjang] }})</option>
          </select>
        </div>
        <div class="form-group">
          <label for="ck-kompetensi">Kompetensi</label>
          <select id="ck-kompetensi" v-model="capaianForm.kompetensi_id">
            <option v-for="k in masterList" :key="k.id" :value="k.id">{{ k.jenis }} - {{ k.nama_kompetensi }} ({{ jenjangLabels[k.jenjang] }})</option>
          </select>
        </div>
        <div class="form-group">
          <label for="ck-penguji">Penguji</label>
          <select id="ck-penguji" v-model="capaianForm.penguji_id">
            <option v-for="a in anggotaList" :key="a.id" :value="a.id">{{ a.nama_lengkap }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-small" @click="showCapaianModal = false">Batal</button>
          <button type="submit" class="btn-submit modal-submit" :disabled="savingCapaian">
            {{ savingCapaian ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.btn-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-gold {
  background: var(--gold);
  border-color: var(--brown);
  color: var(--brown);
}

.btn-gold:hover {
  background: #b7950b;
}

.section-title {
  color: var(--brown);
  margin: 1.5rem 0 0.75rem;
  font-size: 1.05rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
</style>
