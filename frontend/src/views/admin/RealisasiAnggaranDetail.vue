<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const apId = Number(route.params.id)

const loading = ref(true)
const errorMessage = ref('')
const infoMessage = ref('')
const alokasi = ref(null)
const realisasi = ref([])

const isAdmin = localStorage.getItem('role') === 'admin'

const showForm = ref(false)
const form = reactive({ tanggal_realisasi: '', jumlah_realisasi: '', keterangan: '' })
const buktiFile = ref(null)
const saving = ref(false)
const formError = ref('')

const statusLabels = { diajukan: 'Diajukan', disetujui: 'Disetujui', ditolak: 'Ditolak' }
const statusClass = { diajukan: 'pending', disetujui: 'approved', ditolak: 'rejected' }

const totalTerpakai = computed(() => alokasi.value?.total_realisasi || 0)
const sisa = computed(() => (alokasi.value?.jumlah_anggaran || 0) - totalTerpakai.value)
const persen = computed(() => alokasi.value?.persen_penyerapan || 0)

onMounted(loadData)

async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [list, rows] = await Promise.all([
      api.get('/admin/anggaran-program'),
      api.get(`/admin/anggaran-program/${apId}/realisasi`)
    ])
    alokasi.value = list.data.find((a) => a.id === apId) || null
    realisasi.value = rows.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data realisasi.'
  } finally {
    loading.value = false
  }
}

function fmtRupiah(n) {
  return 'Rp ' + Number(n || 0).toLocaleString('id-ID')
}

function fmtTanggal(iso) {
  if (!iso) return '-'
  const [y, m, d] = iso.split('-')
  const bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  return `${Number(d)} ${bulan[Number(m) - 1]} ${y}`
}

function barClass(persen) {
  if (persen > 90) return 'serap-merah'
  if (persen >= 70) return 'serap-kuning'
  return 'serap-hijau'
}

async function submitRealisasi() {
  formError.value = ''
  if (!form.tanggal_realisasi || !form.jumlah_realisasi || Number(form.jumlah_realisasi) <= 0 || !form.keterangan.trim()) {
    formError.value = 'Tanggal, jumlah (lebih dari 0), dan keterangan wajib diisi.'
    return
  }
  if (!buktiFile.value) {
    formError.value = 'File bukti (kwitansi/nota) wajib diunggah.'
    return
  }
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('tanggal_realisasi', form.tanggal_realisasi)
    fd.append('jumlah_realisasi', Number(form.jumlah_realisasi))
    fd.append('keterangan', form.keterangan.trim())
    fd.append('bukti', buktiFile.value)
    await api.post(`/admin/anggaran-program/${apId}/realisasi`, fd)
    showForm.value = false
    form.tanggal_realisasi = ''
    form.jumlah_realisasi = ''
    form.keterangan = ''
    buktiFile.value = null
    infoMessage.value = 'Realisasi diajukan dan menunggu review admin.'
    await loadData()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal mengajukan realisasi.'
  } finally {
    saving.value = false
  }
}

async function reviewReal(row, status) {
  if (!window.confirm(status === 'disetujui' ? 'Setujui realisasi ini?' : 'Tolak realisasi ini?')) return
  errorMessage.value = ''
  try {
    await api.patch(`/admin/realisasi/${row.id}/review`, { status, catatan_review: null })
    infoMessage.value = `Realisasi ditandai ${status}.`
    await loadData()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mereview realisasi.'
  }
}
</script>

<template>
  <div class="page">
    <router-link to="/admin/anggaran-alokasi" class="back-link">Kembali ke Alokasi Anggaran</router-link>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>
    <div v-if="loading" class="greeting">Memuat...</div>

    <template v-else-if="alokasi">
      <div class="page-header">
        <div>
          <h2>{{ alokasi.judul_program_kerja }}</h2>
          <p class="greeting">{{ alokasi.nama_bidang }} — Tahun Anggaran {{ alokasi.tahun_anggaran }} · {{ alokasi.sumber_dana }}</p>
        </div>
        <button class="btn-primary btn-add" @click="showForm = true">+ Input Realisasi Baru</button>
      </div>

      <div class="stats-grid anggaran-summary">
        <div class="stat-card">
          <p class="stat-label">Total Alokasi</p>
          <p class="stat-value">{{ fmtRupiah(alokasi.jumlah_anggaran) }}</p>
        </div>
        <div class="stat-card">
          <p class="stat-label">Realisasi Disetujui</p>
          <p class="stat-value">{{ fmtRupiah(totalTerpakai) }}</p>
        </div>
        <div class="stat-card">
          <p class="stat-label">Sisa Anggaran</p>
          <p class="stat-value">{{ fmtRupiah(sisa) }}</p>
        </div>
        <div class="stat-card">
          <p class="stat-label">Persentase Penyerapan</p>
          <p class="stat-value serap-besar" :class="barClass(persen)">{{ persen }}%</p>
          <div class="serap-bar big">
            <div class="serap-fill" :class="barClass(persen)" :style="{ width: Math.min(100, persen) + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="table-card">
        <h3 class="card-title">Riwayat Realisasi</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Tanggal</th>
              <th>Keterangan</th>
              <th>Jumlah</th>
              <th>Status</th>
              <th>Bukti</th>
              <th v-if="isAdmin">Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in realisasi" :key="r.id">
              <td>{{ fmtTanggal(r.tanggal_realisasi) }}</td>
              <td>{{ r.keterangan }}</td>
              <td>{{ fmtRupiah(r.jumlah_realisasi) }}</td>
              <td>
                <span class="badge-status" :class="statusClass[r.status]">{{ statusLabels[r.status] }}</span>
                <div v-if="r.catatan_review" class="text-muted small">Catatan: {{ r.catatan_review }}</div>
              </td>
              <td>
                <a :href="`http://localhost:8000${r.bukti_url}`" target="_blank" class="link-inline">Lihat bukti</a>
              </td>
              <td v-if="isAdmin">
                <div v-if="r.status === 'diajukan'" class="action-cell">
                  <button class="btn-small btn-submit" @click="reviewReal(r, 'disetujui')">Setujui</button>
                  <button class="btn-small btn-danger" @click="reviewReal(r, 'ditolak')">Tolak</button>
                </div>
                <span v-else class="text-muted small">{{ r.nama_direview || '-' }}</span>
              </td>
            </tr>
            <tr v-if="!realisasi.length">
              <td colspan="6" class="empty-row">Belum ada realisasi untuk alokasi ini.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
        <div class="modal-card">
          <h3>Input Realisasi Baru</h3>
          <div v-if="formError" class="alert-error">{{ formError }}</div>
          <p class="greeting">Sisa anggaran: {{ fmtRupiah(sisa) }}. Jumlah diajukan tidak boleh melebihi sisa.</p>
          <div class="form-group">
            <label>Tanggal Realisasi</label>
            <input v-model="form.tanggal_realisasi" type="date" />
          </div>
          <div class="form-group">
            <label>Jumlah Realisasi (Rp)</label>
            <input v-model.number="form.jumlah_realisasi" type="number" min="1" placeholder="contoh: 5000000" />
          </div>
          <div class="form-group">
            <label>Keterangan Penggunaan Dana</label>
            <textarea v-model="form.keterangan" rows="3" placeholder="Deskripsi penggunaan dana"></textarea>
          </div>
          <div class="form-group">
            <label>File Bukti (wajib)</label>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" @change="buktiFile = $event.target.files[0]" />
          </div>
          <div class="modal-actions">
            <button class="btn-small" @click="showForm = false">Batal</button>
            <button class="btn-submit modal-submit" :disabled="saving" @click="submitRealisasi">
              {{ saving ? 'Menyimpan...' : 'Ajukan Realisasi' }}
            </button>
          </div>
        </div>
      </div>
    </template>
    <p v-else-if="!loading" class="greeting">Alokasi anggaran tidak ditemukan.</p>
  </div>
</template>
