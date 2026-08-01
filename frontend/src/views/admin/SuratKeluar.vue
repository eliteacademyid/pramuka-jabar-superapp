<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import {
  approveSuratKeluar,
  createSuratKeluar,
  deleteLampiran,
  deleteSuratKeluar,
  downloadLampiranUrl,
  getSuratKeluar,
  getSuratKeluarDetail,
  getTracking,
  updateSuratKeluar,
  uploadLampiran,
} from '../../services/surat'

const router = useRouter()

// ─── State ──────────────────────────────────────────────────────────────────
const surats = ref([])
const loading = ref(true)
const errorMessage = ref('')
const searchQuery = ref('')
const filterStatus = ref('')

const STATUS_OPTIONS = ['Draft', 'Diverifikasi', 'Didisposisi', 'Diproses', 'Selesai', 'Diarsipkan']

// Modal Form
const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({
  tujuan: '', tanggal_surat: '', perihal: '', isi: '',
})

// Modal Detail
const showDetail = ref(false)
const detailSurat = ref(null)
const trackingLogs = ref([])
const loadingDetail = ref(false)

// File Upload
const uploadSuratId = ref(null)
const uploadingFile = ref(false)
const fileInputRef = ref(null)

const approvingId = ref(null)

// ─── Load ────────────────────────────────────────────────────────────────────
onMounted(loadData)

async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (searchQuery.value) params.search = searchQuery.value
    const res = await getSuratKeluar(params)
    surats.value = res.data
  } catch (err) {
    if (err.response?.status === 401) { localStorage.removeItem('token'); router.push({ name: 'login' }) }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data surat keluar.'
  } finally {
    loading.value = false
  }
}

// ─── Form ─────────────────────────────────────────────────────────────────────
function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.value = { tujuan: '', tanggal_surat: '', perihal: '', isi: '' }
  formError.value = ''
  showModal.value = true
}

function openEdit(s) {
  isEdit.value = true
  editingId.value = s.id
  form.value = {
    tujuan: s.tujuan || '',
    tanggal_surat: s.tanggal_surat || '',
    perihal: s.perihal || '',
    isi: s.isi || '',
  }
  formError.value = ''
  showModal.value = true
}

async function saveSurat() {
  formError.value = ''
  saving.value = true
  try {
    if (isEdit.value) {
      await updateSuratKeluar(editingId.value, form.value)
    } else {
      await createSuratKeluar(form.value)
    }
    showModal.value = false
    await loadData()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan surat.'
  } finally {
    saving.value = false
  }
}

async function hapusSurat(s) {
  if (!window.confirm(`Hapus surat "${s.perihal}"?`)) return
  try {
    await deleteSuratKeluar(s.id)
    await loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus surat.')
  }
}

// ─── Approve ─────────────────────────────────────────────────────────────────
async function approveSurat(s) {
  if (!window.confirm(`Approve surat "${s.perihal}"? Nomor surat akan di-generate otomatis.`)) return
  approvingId.value = s.id
  try {
    await approveSuratKeluar(s.id)
    await loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal approve surat.')
  } finally {
    approvingId.value = null
  }
}

// ─── Detail ────────────────────────────────────────────────────────────────
async function openDetail(s) {
  showDetail.value = true
  loadingDetail.value = true
  detailSurat.value = null
  trackingLogs.value = []
  try {
    const [detailRes, trackRes] = await Promise.all([
      getSuratKeluarDetail(s.id),
      getTracking(s.id),
    ])
    detailSurat.value = detailRes.data
    trackingLogs.value = trackRes.data
  } catch {
    alert('Gagal memuat detail surat.')
    showDetail.value = false
  } finally {
    loadingDetail.value = false
  }
}

// ─── Lampiran ────────────────────────────────────────────────────────────────
function triggerUpload(suratId) {
  uploadSuratId.value = suratId
  fileInputRef.value?.click()
}

async function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  uploadingFile.value = true
  try {
    await uploadLampiran(uploadSuratId.value, file)
    if (showDetail.value && detailSurat.value?.id === uploadSuratId.value) {
      const res = await getSuratKeluarDetail(uploadSuratId.value)
      detailSurat.value = res.data
    }
    await loadData()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengunggah lampiran.')
  } finally {
    uploadingFile.value = false
    event.target.value = ''
  }
}

async function hapusLampiran(id) {
  if (!window.confirm('Hapus lampiran ini?')) return
  try {
    await deleteLampiran(id)
    if (showDetail.value && detailSurat.value) {
      const res = await getSuratKeluarDetail(detailSurat.value.id)
      detailSurat.value = res.data
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus lampiran.')
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function statusClass(s) {
  const map = {
    'Draft': 'badge-status draft',
    'Diverifikasi': 'badge-status verified',
    'Didisposisi': 'badge-status disposisi',
    'Diproses': 'badge-status proses',
    'Selesai': 'badge-status selesai',
    'Diarsipkan': 'badge-status arsip',
  }
  return map[s] || 'badge-status'
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateTime(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function fileSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<template>
  <div class="dashboard-content">
    <input ref="fileInputRef" type="file" accept=".pdf,.docx,.xlsx,.jpg,.jpeg,.png"
      style="display:none" @change="handleFileUpload" />

    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Surat Keluar</h2>
        <p class="greeting">Buat dan kelola surat keluar organisasi.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Buat Surat Keluar</button>
    </div>

    <!-- Filter & Search -->
    <div class="filter-bar">
      <input v-model="searchQuery" class="search-input" type="text"
        placeholder="Cari nomor, perihal, tujuan..." @keyup.enter="loadData" />
      <select v-model="filterStatus" class="filter-select" @change="loadData">
        <option value="">Semua Status</option>
        <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</option>
      </select>
      <button class="btn-small" @click="loadData">Cari</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <!-- Table -->
    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>No. Surat</th>
            <th>Tujuan</th>
            <th>Perihal</th>
            <th>Tgl Surat</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in surats" :key="s.id">
            <td>{{ s.nomor_surat || <span class="text-muted">Belum di-generate</span> }}</td>
            <td>{{ s.tujuan || '-' }}</td>
            <td class="td-perihal">{{ s.perihal }}</td>
            <td>{{ formatDate(s.tanggal_surat) }}</td>
            <td><span :class="statusClass(s.status)">{{ s.status }}</span></td>
            <td class="td-actions">
              <button class="btn-small" @click="openDetail(s)">Detail</button>
              <button class="btn-small btn-info" @click="openEdit(s)">Edit</button>
              <button v-if="s.status === 'Draft'" class="btn-small btn-approve"
                @click="approveSurat(s)" :disabled="approvingId === s.id">
                {{ approvingId === s.id ? '...' : 'Approve' }}
              </button>
              <button class="btn-small" @click="triggerUpload(s.id)" :disabled="uploadingFile">Lampiran</button>
              <button class="btn-small btn-danger" @click="hapusSurat(s)">Hapus</button>
            </td>
          </tr>
          <tr v-if="surats.length === 0">
            <td colspan="6" class="empty-row">Belum ada surat keluar.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <!-- ─── Modal Form ─────────────────────────────────────────────────────── -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <form class="modal-card modal-wide" @submit.prevent="saveSurat">
        <h3>{{ isEdit ? 'Edit Surat Keluar' : 'Buat Surat Keluar (Draft)' }}</h3>
        <div v-if="formError" class="alert-error">{{ formError }}</div>

        <div class="form-row">
          <div class="form-group">
            <label>Tujuan</label>
            <input v-model="form.tujuan" type="text" placeholder="Nama instansi/tujuan" />
          </div>
          <div class="form-group">
            <label>Tanggal Surat</label>
            <input v-model="form.tanggal_surat" type="date" />
          </div>
        </div>
        <div class="form-group">
          <label>Perihal <span class="required">*</span></label>
          <input v-model="form.perihal" type="text" required placeholder="Perihal surat" />
        </div>
        <div class="form-group">
          <label>Isi / Ringkasan</label>
          <textarea v-model="form.isi" rows="4" placeholder="Isi surat..."></textarea>
        </div>

        <div class="info-box">
          <span>💡</span> Nomor surat akan di-generate otomatis saat di-<strong>Approve</strong>.
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-small" @click="showModal = false">Batal</button>
          <button type="submit" class="btn-submit modal-submit" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan Draft' }}
          </button>
        </div>
      </form>
    </div>

    <!-- ─── Modal Detail ──────────────────────────────────────────────────── -->
    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal-card modal-detail">
        <div class="detail-header">
          <h3>Detail Surat Keluar</h3>
          <button class="btn-close" @click="showDetail = false">✕</button>
        </div>

        <div v-if="loadingDetail" class="loading-text">Memuat detail...</div>
        <div v-else-if="detailSurat">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">No. Surat</span>
              <span>{{ detailSurat.nomor_surat || '(belum di-generate)' }}</span>
            </div>
            <div class="detail-item"><span class="detail-label">Status</span><span :class="statusClass(detailSurat.status)">{{ detailSurat.status }}</span></div>
            <div class="detail-item"><span class="detail-label">Tujuan</span><span>{{ detailSurat.tujuan || '-' }}</span></div>
            <div class="detail-item"><span class="detail-label">Tgl Surat</span><span>{{ formatDate(detailSurat.tanggal_surat) }}</span></div>
            <div class="detail-item full-width"><span class="detail-label">Perihal</span><span>{{ detailSurat.perihal }}</span></div>
            <div class="detail-item full-width" v-if="detailSurat.isi"><span class="detail-label">Isi</span><span>{{ detailSurat.isi }}</span></div>
          </div>

          <div class="section-title">
            <span>Lampiran</span>
            <button class="btn-small" @click="triggerUpload(detailSurat.id)">+ Upload</button>
          </div>
          <div v-if="detailSurat.lampiran?.length" class="lampiran-list">
            <div v-for="l in detailSurat.lampiran" :key="l.id" class="lampiran-item">
              <span class="lampiran-name">{{ l.nama_file }}</span>
              <span class="lampiran-size">{{ fileSize(l.ukuran_file) }}</span>
              <div class="lampiran-actions">
                <a :href="downloadLampiranUrl(l.id)" target="_blank" class="btn-small">Unduh</a>
                <button class="btn-small btn-danger" @click="hapusLampiran(l.id)">Hapus</button>
              </div>
            </div>
          </div>
          <p v-else class="empty-text">Belum ada lampiran.</p>

          <div class="section-title"><span>Riwayat Aktivitas</span></div>
          <div class="timeline">
            <div v-for="log in trackingLogs" :key="log.id" class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-activity">{{ log.aktivitas }}</div>
                <div class="timeline-meta">
                  <span>{{ log.user_info?.nama_lengkap || 'Sistem' }}</span>
                  <span>{{ formatDateTime(log.created_at) }}</span>
                </div>
                <div v-if="log.keterangan" class="timeline-note">{{ log.keterangan }}</div>
              </div>
            </div>
            <div v-if="!trackingLogs.length" class="empty-text">Belum ada riwayat.</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
