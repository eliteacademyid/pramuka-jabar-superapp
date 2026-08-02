<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const item = ref(null)
const users = ref([])

const showDisposisi = ref(false)
const dispoForm = ref({ kepada_user_id: '', instruksi: 'untuk_ditindaklanjuti', catatan: '' })
const dispoError = ref('')
const savingDispo = ref(false)
const successMessage = ref('')

const instruksiList = [
  { value: 'untuk_diketahui', label: 'Untuk Diketahui' },
  { value: 'untuk_ditindaklanjuti', label: 'Untuk Ditindaklanjuti' },
  { value: 'untuk_disposisi_lanjut', label: 'Untuk Disposisi Lanjut' },
  { value: 'untuk_rapat', label: 'Untuk Rapat' },
  { value: 'lainnya', label: 'Lainnya' }
]

const sifatLabels = {
  biasa: 'Biasa',
  penting: 'Penting',
  segera: 'Segera',
  rahasia: 'Rahasia'
}
const statusLabels = {
  baru: 'Baru',
  didisposisikan: 'Didisposisikan',
  selesai: 'Selesai',
  diarsipkan: 'Diarsipkan'
}
const dispoStatusLabels = {
  menunggu: 'Menunggu',
  diproses: 'Diproses',
  selesai: 'Selesai'
}

onMounted(async () => {
  await loadDetail()
  await loadUsers()
})

async function loadDetail() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get(`/admin/surat-masuk/${route.params.id}`)
    item.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat detail surat.'
  } finally {
    loading.value = false
  }
}

async function loadUsers() {
  try {
    const res = await api.get('/admin/users')
    users.value = res.data.filter((u) => u.is_active && (u.role === 'admin' || u.role === 'staff'))
  } catch {
    /* optional */
  }
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

async function buatDisposisi() {
  dispoError.value = ''
  if (!dispoForm.value.kepada_user_id) {
    dispoError.value = 'Pilih user tujuan disposisi.'
    return
  }
  savingDispo.value = true
  try {
    await api.post(`/admin/surat-masuk/${item.value.id}/disposisi`, dispoForm.value)
    showDisposisi.value = false
    successMessage.value = 'Disposisi berhasil dibuat.'
    dispoForm.value = { kepada_user_id: '', instruksi: 'untuk_ditindaklanjuti', catatan: '' }
    await loadDetail()
  } catch (err) {
    dispoError.value = err.response?.data?.detail || 'Gagal membuat disposisi.'
  } finally {
    savingDispo.value = false
  }
}

function openEdit() {
  router.push({ name: 'admin-surat-masuk-baru', query: { edit: item.value.id } })
}
</script>

<template>
  <div class="page">
    <router-link to="/admin/surat-masuk" class="back-link">Kembali ke Surat Masuk</router-link>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert-success">{{ successMessage }}</div>
    <div v-if="loading" class="greeting">Memuat...</div>

    <template v-else-if="item">
      <div class="page-header">
        <div>
          <h2>{{ item.nomor_agenda }}</h2>
          <p class="greeting">{{ item.perihal }}</p>
        </div>
        <div class="header-actions">
          <span class="badge-status" :class="item.status">{{ statusLabels[item.status] }}</span>
          <span :class="sifatBadgeClass(item.sifat)">{{ sifatLabels[item.sifat] }}</span>
          <button class="btn-primary btn-add" @click="openEdit">Edit Surat</button>
        </div>
      </div>

      <div class="table-card">
        <table class="data-table detail-table">
          <tbody>
            <tr><th>Pengirim</th><td>{{ item.pengirim }}</td></tr>
            <tr><th>Nomor Surat Asal</th><td>{{ item.nomor_surat_asal || '-' }}</td></tr>
            <tr><th>Tanggal Surat</th><td>{{ fmtTanggal(item.tanggal_surat) }}</td></tr>
            <tr><th>Tanggal Diterima</th><td>{{ fmtTanggal(item.tanggal_diterima) }}</td></tr>
            <tr><th>Klasifikasi</th><td>{{ item.nama_klasifikasi }}</td></tr>
            <tr><th>Sifat</th><td>{{ sifatLabels[item.sifat] }}</td></tr>
            <tr><th>Diinput Oleh</th><td>{{ item.nama_diinput }}</td></tr>
            <tr><th>File Scan</th>
              <td>
                <a v-if="item.file_scan_url" :href="`http://localhost:8000${item.file_scan_url}`" target="_blank" class="link-inline">
                  Buka file scan
                </a>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="page-header" style="margin-top: 1.5rem">
        <div>
          <h3>Timeline Disposisi</h3>
          <p class="greeting">Riwayat alur disposisi surat ini (berurutan).</p>
        </div>
        <button class="btn-primary btn-add" @click="showDisposisi = true">+ Buat Disposisi Baru</button>
      </div>

      <div v-if="!item.disposisi?.length" class="greeting">Belum ada disposisi untuk surat ini.</div>

      <div v-else class="dispo-timeline">
        <div v-for="d in item.disposisi" :key="d.id" class="dispo-item">
          <div class="dispo-head">
            <span class="badge-status neutral">{{ dispoStatusLabels[d.status] }}</span>
            <span class="text-muted small">{{ fmtTanggal(d.tanggal_disposisi) }}</span>
          </div>
          <p class="dispo-flow">
            <strong>{{ d.nama_dari }}</strong> → <strong>{{ d.nama_kepada }}</strong>
          </p>
          <p class="dispo-instruksi">
            <span class="badge-status neutral">{{ instruksiList.find((i) => i.value === d.instruksi)?.label || d.instruksi }}</span>
          </p>
          <p v-if="d.catatan" class="text-muted">Catatan: {{ d.catatan }}</p>
          <p v-if="d.status === 'selesai'" class="dispo-done">
            ✔ Selesai {{ fmtTanggal(d.tanggal_selesai) }} — {{ d.catatan_penyelesaian }}
          </p>
        </div>
      </div>

      <div v-if="showDisposisi" class="modal-overlay" @click.self="showDisposisi = false">
        <div class="modal-card">
          <h3>Buat Disposisi Baru</h3>
          <div v-if="dispoError" class="alert-error">{{ dispoError }}</div>
          <div class="form-group">
            <label>User Tujuan</label>
            <select v-model="dispoForm.kepada_user_id">
              <option value="">-- Pilih User --</option>
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.nama_lengkap }} ({{ u.role }})</option>
            </select>
          </div>
          <div class="form-group">
            <label>Instruksi</label>
            <select v-model="dispoForm.instruksi">
              <option v-for="i in instruksiList" :key="i.value" :value="i.value">{{ i.label }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Catatan</label>
            <textarea v-model="dispoForm.catatan" rows="3" placeholder="Catatan tambahan..."></textarea>
          </div>
          <div class="modal-actions">
            <button class="btn-small" @click="showDisposisi = false">Batal</button>
            <button class="btn-submit modal-submit" :disabled="savingDispo" @click="buatDisposisi">
              {{ savingDispo ? 'Menyimpan...' : 'Kirim Disposisi' }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
