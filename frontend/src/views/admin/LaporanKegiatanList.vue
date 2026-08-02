<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const items = ref([])
const loading = ref(true)
const errorMessage = ref('')
const infoMessage = ref('')

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/laporan-kegiatan')
    items.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat laporan kegiatan.'
  } finally {
    loading.value = false
  }
}

function fmtTanggal(iso) {
  if (!iso) return '-'
  const [y, m, d] = iso.split('-')
  const bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  return `${Number(d)} ${bulan[Number(m) - 1]} ${y}`
}

function openEdit(item) {
  router.push({ name: 'admin-laporan-kegiatan-edit', params: { id: item.id } })
}

async function hapusLaporan(item) {
  if (!window.confirm(`Hapus laporan "${item.judul_laporan}"?`)) return
  try {
    await api.delete(`/admin/laporan-kegiatan/${item.id}`)
    infoMessage.value = 'Laporan dihapus.'
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menghapus laporan.'
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Laporan Kegiatan</h2>
        <p class="greeting">Laporan pelaksanaan untuk kegiatan yang sudah selesai.</p>
      </div>
      <router-link to="/admin/laporan-kegiatan/baru" class="btn-primary btn-add">
        + Buat Laporan
      </router-link>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>

    <div v-if="loading" class="greeting">Memuat...</div>
    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Kegiatan</th>
            <th>Judul Laporan</th>
            <th>Tanggal</th>
            <th>Peserta</th>
            <th>Dibuat Oleh</th>
            <th>File</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in items" :key="l.id">
            <td>{{ l.nama_kegiatan }}</td>
            <td>{{ l.judul_laporan }}</td>
            <td>{{ fmtTanggal(l.tanggal_laporan) }}</td>
            <td>{{ l.jumlah_peserta ?? '-' }}</td>
            <td>{{ l.nama_dibuat }}</td>
            <td>
              <a :href="`http://localhost:8000${l.file_laporan_url}`" target="_blank" class="link-inline">Buka file</a>
            </td>
            <td>
              <div class="action-cell">
                <button class="btn-small" @click="openEdit(l)">Edit</button>
                <button class="btn-small btn-danger" @click="hapusLaporan(l)">Hapus</button>
              </div>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="7" class="empty-row">Belum ada laporan kegiatan.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
