<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const tab = ref('menunggu')
const items = ref([])
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const selected = ref(null)
const catatan = ref('')
const completing = ref(false)

const tabs = [
  { key: 'menunggu', label: 'Menunggu' },
  { key: 'diproses', label: 'Diproses' },
  { key: 'selesai', label: 'Selesai' }
]

const instruksiLabels = {
  untuk_diketahui: 'Untuk Diketahui',
  untuk_ditindaklanjuti: 'Untuk Ditindaklanjuti',
  untuk_disposisi_lanjut: 'Untuk Disposisi Lanjut',
  untuk_rapat: 'Untuk Rapat',
  lainnya: 'Lainnya'
}

const countByTab = computed(() => {
  const c = { menunggu: 0, diproses: 0, selesai: 0 }
  items.value.forEach((i) => {
    if (i.status in c) c[i.status] += 1
  })
  return c
})

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/disposisi/saya')
    items.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat disposisi.'
  } finally {
    loading.value = false
  }
}

function visibleItems() {
  return items.value.filter((i) => i.status === tab.value)
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

async function prosesDisposisi(d) {
  try {
    await api.patch(`/admin/disposisi/${d.id}/proses`)
    successMessage.value = 'Disposisi ditandai diproses.'
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memproses.'
  }
}

function openCompleteModal(d) {
  selected.value = d
  catatan.value = ''
}

async function tandaiSelesai() {
  if (!catatan.value.trim()) {
    errorMessage.value = 'Catatan penyelesaian wajib diisi.'
    return
  }
  completing.value = true
  try {
    await api.patch(`/admin/disposisi/${selected.value.id}/selesai`, {
      catatan_penyelesaian: catatan.value
    })
    selected.value = null
    successMessage.value = 'Disposisi ditandai selesai.'
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menandai selesai.'
  } finally {
    completing.value = false
  }
}

function openSurat(d) {
  router.push({ name: 'admin-surat-masuk-detail', params: { id: d.surat.id } })
}

onMounted(loadItems)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Disposisi Untuk Saya</h2>
        <p class="greeting">Surat yang didisposisikan kepada Anda.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert-success">{{ successMessage }}</div>

    <div class="tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab"
        :class="{ active: tab === t.key }"
        @click="tab = t.key"
      >
        {{ t.label }} ({{ countByTab[t.key] }})
      </button>
    </div>

    <div v-if="loading" class="greeting">Memuat...</div>
    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Nomor Agenda</th>
            <th>Perihal Surat</th>
            <th>Dari</th>
            <th>Instruksi</th>
            <th>Sifat</th>
            <th>Tanggal</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in visibleItems()" :key="d.id">
            <td>{{ d.surat.nomor_agenda }}</td>
            <td>{{ d.surat.perihal }}</td>
            <td>{{ d.nama_dari }}</td>
            <td>{{ instruksiLabels[d.instruksi] || d.instruksi }}</td>
            <td><span :class="sifatBadgeClass(d.surat.sifat)">{{ d.surat.sifat }}</span></td>
            <td>{{ fmtTanggal(d.tanggal_disposisi) }}</td>
            <td>
              <div class="action-cell">
                <button class="btn-small" @click="openSurat(d)">Lihat</button>
                <template v-if="tab === 'menunggu'">
                  <button class="btn-small" @click="prosesDisposisi(d)">Proses</button>
                  <button class="btn-small btn-submit" @click="openCompleteModal(d)">Selesai</button>
                </template>
                <button v-if="tab === 'diproses'" class="btn-small btn-submit" @click="openCompleteModal(d)">
                  Selesaikan
                </button>
                <span v-if="d.catatan_penyelesaian" class="text-muted small">✔ {{ d.catatan_penyelesaian }}</span>
              </div>
            </td>
          </tr>
          <tr v-if="!visibleItems().length">
            <td colspan="7" class="empty-row">Tidak ada disposisi berstatus {{ tab }}.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="selected" class="modal-overlay" @click.self="selected = null">
      <div class="modal-card">
        <h3>Selesaikan Disposisi</h3>
        <p class="greeting">
          {{ selected.surat.nomor_agenda }} — {{ selected.surat.perihal }}
        </p>
        <div class="form-group">
          <label>Catatan Penyelesaian</label>
          <textarea v-model="catatan" rows="3" placeholder="Contoh: sudah dijawab, sudah disampaikan ke bidang..."></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn-small" @click="selected = null">Batal</button>
          <button class="btn-submit modal-submit" :disabled="completing" @click="tandaiSelesai">
            {{ completing ? 'Menyimpan...' : 'Tandai Selesai' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
