<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const currentUser = ref(null)
const kegiatanList = ref([])
const loading = ref(true)
const errorMessage = ref('')
const userOptions = ref([])

const statusOptions = ['direncanakan', 'berlangsung', 'selesai', 'dibatalkan']

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({
  nama_kegiatan: '',
  deskripsi: '',
  tanggal_mulai: '',
  tanggal_selesai: '',
  penanggung_jawab_id: ''
})
const formError = ref('')
const saving = ref(false)

const showDokModal = ref(false)
const dokKegiatanId = ref(null)
const dokCatatan = ref('')
const dokFiles = ref([])
const dokLoading = ref(false)
const dokKegiatanNama = ref('')

onMounted(() => {
  loadCurrentUser()
  loadKegiatan()
  loadUsers()
})

async function loadCurrentUser() {
  try {
    const res = await api.get('/auth/me')
    currentUser.value = res.data
  } catch {
    /* handled by layout guard */
  }
}

async function loadKegiatan() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/kegiatan')
    kegiatanList.value = res.data
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
      return
    }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data kegiatan.'
  } finally {
    loading.value = false
  }
}

async function loadUsers() {
  try {
    const res = await api.get('/admin/users')
    userOptions.value = res.data.filter((u) => u.is_active)
  } catch {
    /* abaikan */
  }
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.value = {
    nama_kegiatan: '',
    deskripsi: '',
    tanggal_mulai: '',
    tanggal_selesai: '',
    penanggung_jawab_id: ''
  }
  formError.value = ''
  showModal.value = true
}

function openEdit(kegiatan) {
  isEdit.value = true
  editingId.value = kegiatan.id
  form.value = {
    nama_kegiatan: kegiatan.nama_kegiatan,
    deskripsi: kegiatan.deskripsi || '',
    tanggal_mulai: kegiatan.tanggal_mulai,
    tanggal_selesai: kegiatan.tanggal_selesai,
    penanggung_jawab_id: kegiatan.penanggung_jawab_id
  }
  formError.value = ''
  showModal.value = true
}

async function saveKegiatan() {
  formError.value = ''
  saving.value = true
  try {
    const payload = {
      nama_kegiatan: form.value.nama_kegiatan,
      deskripsi: form.value.deskripsi || null,
      tanggal_mulai: form.value.tanggal_mulai,
      tanggal_selesai: form.value.tanggal_selesai,
      penanggung_jawab_id: Number(form.value.penanggung_jawab_id)
    }
    if (isEdit.value) {
      await api.put(`/kegiatan/${editingId.value}`, payload)
    } else {
      await api.post('/kegiatan', payload)
    }
    showModal.value = false
    await loadKegiatan()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan kegiatan.'
  } finally {
    saving.value = false
  }
}

async function deleteKegiatan(kegiatan) {
  if (!window.confirm(`Hapus kegiatan "${kegiatan.nama_kegiatan}"?`)) return
  try {
    await api.delete(`/kegiatan/${kegiatan.id}`)
    await loadKegiatan()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus kegiatan.')
  }
}

async function updateStatus(kegiatan, newStatus) {
  try {
    await api.patch(`/kegiatan/${kegiatan.id}/status`, { status: newStatus })
    await loadKegiatan()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengubah status.')
    await loadKegiatan()
  }
}

function canEditStatus(kegiatan) {
  if (!currentUser.value) return false
  if (currentUser.value.role === 'admin') return true
  return kegiatan.penanggung_jawab_id === currentUser.value.id
}

async function openDokModal(kegiatan) {
  dokKegiatanId.value = kegiatan.id
  dokKegiatanNama.value = kegiatan.nama_kegiatan
  dokCatatan.value = ''
  dokFiles.value = []
  dokLoading.value = true
  showDokModal.value = true
  try {
    const res = await api.get(`/kegiatan/${kegiatan.id}`)
    const dok = res.data.dokumentasi
    if (dok) {
      dokCatatan.value = dok.catatan || ''
      dokFiles.value = dok.files || []
    }
  } catch {
    /* abaikan - mungkin belum ada dokumentasi */
  } finally {
    dokLoading.value = false
  }
}

async function saveCatatan() {
  try {
    await api.put(`/kegiatan/${dokKegiatanId.value}/dokumentasi`, {
      catatan: dokCatatan.value || null
    })
    alert('Catatan berhasil disimpan.')
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menyimpan catatan.')
  }
}

async function uploadFile(e) {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    await api.post(`/kegiatan/${dokKegiatanId.value}/dokumentasi/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    e.target.value = ''
    const res = await api.get(`/kegiatan/${dokKegiatanId.value}`)
    const dok = res.data.dokumentasi
    if (dok) {
      dokFiles.value = dok.files || []
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengunggah file.')
  }
}

async function deleteFile(fileId) {
  if (!window.confirm('Hapus file ini?')) return
  try {
    await api.delete(`/kegiatan/${dokKegiatanId.value}/dokumentasi/files/${fileId}`)
    dokFiles.value = dokFiles.value.filter((f) => f.id !== fileId)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus file.')
  }
}

function statusBadgeClass(status) {
  switch (status) {
    case 'direncanakan': return 'badge badge-blue'
    case 'berlangsung': return 'badge badge-amber'
    case 'selesai': return 'badge badge-green'
    case 'dibatalkan': return 'badge badge-red'
    default: return 'badge'
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

function getPJName(kegiatan) {
  return kegiatan.penanggung_jawab?.nama_lengkap || '—'
}

function getFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Program Kegiatan</h2>
        <p class="greeting">Kelola program kerja dan agenda internal Kwarda.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Tambah Kegiatan</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="loading" class="greeting">Memuat data kegiatan...</div>

    <div v-else-if="kegiatanList.length === 0" class="table-card" style="text-align:center;padding:2rem;">
      <p>Belum ada kegiatan. Tambahkan kegiatan pertama.</p>
    </div>

    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nama Kegiatan</th>
            <th>Tanggal</th>
            <th>Penanggung Jawab</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="k in kegiatanList" :key="k.id">
            <td>{{ k.id }}</td>
            <td>{{ k.nama_kegiatan }}</td>
            <td>{{ formatDate(k.tanggal_mulai) }} — {{ formatDate(k.tanggal_selesai) }}</td>
            <td>{{ getPJName(k) }}</td>
            <td>
              <select
                class="status-dropdown"
                v-model="k.status"
                @change="updateStatus(k, k.status)"
                :disabled="!canEditStatus(k)"
              >
                <option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</option>
              </select>
              <span :class="statusBadgeClass(k.status)">{{ k.status }}</span>
            </td>
            <td>
              <button class="btn-small" @click="openDokModal(k)">Dok</button>
              <button class="btn-small" @click="openEdit(k)">Edit</button>
              <button class="btn-small btn-danger" @click="deleteKegiatan(k)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <form class="modal-card" @submit.prevent="saveKegiatan">
        <h3>{{ isEdit ? 'Edit Kegiatan' : 'Tambah Kegiatan' }}</h3>

        <div v-if="formError" class="alert-error">{{ formError }}</div>

        <div class="form-group">
          <label for="modal-nama">Nama Kegiatan</label>
          <input id="modal-nama" v-model="form.nama_kegiatan" type="text" required />
        </div>

        <div class="form-group">
          <label for="modal-deskripsi">Deskripsi</label>
          <input id="modal-deskripsi" v-model="form.deskripsi" type="text" />
        </div>

        <div class="form-group">
          <label for="modal-tgl-mulai">Tanggal Mulai</label>
          <input id="modal-tgl-mulai" v-model="form.tanggal_mulai" type="date" required />
        </div>

        <div class="form-group">
          <label for="modal-tgl-selesai">Tanggal Selesai</label>
          <input id="modal-tgl-selesai" v-model="form.tanggal_selesai" type="date" required />
        </div>

        <div class="form-group">
          <label for="modal-pj">Penanggung Jawab</label>
          <select id="modal-pj" v-model="form.penanggung_jawab_id" required>
            <option value="" disabled>Pilih penanggung jawab</option>
            <option v-for="u in userOptions" :key="u.id" :value="u.id">
              {{ u.nama_lengkap }} ({{ u.role }})
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-small" @click="showModal = false">Batal</button>
          <button type="submit" class="btn-submit modal-submit" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>

    <div v-if="showDokModal" class="modal-overlay" @click.self="showDokModal = false">
      <div class="modal-card">
        <h3>Dokumentasi: {{ dokKegiatanNama }}</h3>

        <p v-if="dokLoading" class="greeting">Memuat...</p>

        <template v-else>
          <div class="form-group">
            <label for="dok-catatan">Catatan Hasil Kegiatan</label>
            <textarea
              id="dok-catatan"
              v-model="dokCatatan"
              rows="4"
              style="width:100%;padding:0.5rem;border:1px solid #ccc;border-radius:4px;"
            ></textarea>
          </div>

          <div class="modal-actions" style="margin-bottom:1rem;">
            <button class="btn-submit modal-submit" @click="saveCatatan">Simpan Catatan</button>
          </div>

          <div class="form-group">
            <label>File Dokumentasi</label>
            <div class="file-list">
              <div v-if="dokFiles.length === 0" class="file-item" style="color:#999;">
                Belum ada file.
              </div>
              <div v-for="f in dokFiles" :key="f.id" class="file-item">
                <span class="file-info">
                  {{ f.nama_file }} ({{ getFileSize(f.ukuran) }})
                </span>
                <button class="btn-small" @click="deleteFile(f.id)">Hapus</button>
              </div>
            </div>
          </div>

          <div class="form-group upload-area">
            <label for="dok-file">Unggah File Baru (max 5MB: PDF, JPG, PNG, DOCX)</label>
            <input
              id="dok-file"
              type="file"
              accept=".pdf,.jpg,.jpeg,.png,.docx"
              @change="uploadFile"
              style="margin-top:0.5rem;"
            />
          </div>
        </template>

        <div class="modal-actions" style="margin-top:1rem;">
          <button class="btn-small" @click="showDokModal = false">Tutup</button>
        </div>
      </div>
    </div>
  </div>
</template>
