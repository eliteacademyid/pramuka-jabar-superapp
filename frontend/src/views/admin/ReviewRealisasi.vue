<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const isAdmin = localStorage.getItem('role') === 'admin'

const items = ref([])
const loading = ref(true)
const errorMessage = ref('')
const infoMessage = ref('')

const selected = ref(null)
const catatan = ref('')
const rejecting = ref(false)

const statusLabels = { diajukan: 'Diajukan', disetujui: 'Disetujui', ditolak: 'Ditolak' }

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/pelaporan/realisasi-pending')
    items.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat realisasi yang menunggu review.'
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

async function setujui(item) {
  if (!window.confirm(`Setujui realisasi ${fmtRupiah(item.jumlah_realisasi)} untuk "${item.judul_program_kerja}"?`)) return
  try {
    await api.patch(`/admin/realisasi/${item.id}/review`, { status: 'disetujui' })
    infoMessage.value = 'Realisasi disetujui.'
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyetujui realisasi.'
  }
}

function openTolak(item) {
  selected.value = item
  catatan.value = ''
}

async function konfirmasiTolak() {
  if (!catatan.value.trim()) {
    errorMessage.value = 'Catatan review wajib diisi saat menolak.'
    return
  }
  rejecting.value = true
  try {
    await api.patch(`/admin/realisasi/${selected.value.id}/review`, {
      status: 'ditolak',
      catatan_review: catatan.value.trim()
    })
    selected.value = null
    infoMessage.value = 'Realisasi ditolak.'
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menolak realisasi.'
  } finally {
    rejecting.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Review Realisasi Anggaran</h2>
        <p class="greeting">Realisasi berstatus "diajukan" lintas program, prioritas untuk ditinjau.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>
    <div v-if="!isAdmin" class="alert-error">Halaman ini khusus admin. Staf hanya bisa menginput realisasi.</div>

    <div v-if="loading" class="greeting">Memuat...</div>
    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Program Kerja</th>
            <th>Tanggal</th>
            <th>Keterangan</th>
            <th>Jumlah</th>
            <th>Diinput Oleh</th>
            <th>Bukti</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in items" :key="r.id">
            <td>
              {{ r.judul_program_kerja }}
              <div class="text-muted small">{{ r.nama_bidang }} · {{ r.tahun_anggaran }}</div>
            </td>
            <td>{{ fmtTanggal(r.tanggal_realisasi) }}</td>
            <td>{{ r.keterangan }}</td>
            <td>{{ fmtRupiah(r.jumlah_realisasi) }}</td>
            <td>{{ r.nama_diinput }}</td>
            <td>
              <a :href="`http://localhost:8000${r.bukti_url}`" target="_blank" class="link-inline">Preview bukti</a>
            </td>
            <td v-if="isAdmin">
              <div class="action-cell">
                <button class="btn-small btn-submit" @click="setujui(r)">Setujui</button>
                <button class="btn-small btn-danger" @click="openTolak(r)">Tolak</button>
              </div>
            </td>
            <td v-else class="text-muted small">-</td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="7" class="empty-row">Tidak ada realisasi yang menunggu review.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="selected" class="modal-overlay" @click.self="selected = null">
      <div class="modal-card">
        <h3>Tolak Realisasi</h3>
        <p class="greeting">
          {{ selected.judul_program_kerja }} — {{ fmtRupiah(selected.jumlah_realisasi) }} ({{ selected.keterangan }})
        </p>
        <div class="form-group">
          <label>Catatan Review (wajib)</label>
          <textarea v-model="catatan" rows="3" placeholder="Alasan penolakan..."></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn-small" @click="selected = null">Batal</button>
          <button class="btn-submit modal-submit btn-danger" :disabled="rejecting" @click="konfirmasiTolak">
            {{ rejecting ? 'Menyimpan...' : 'Tolak Realisasi' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
