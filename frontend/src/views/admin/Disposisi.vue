<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getDisposisi, updateDisposisi } from '../../services/surat'

const router = useRouter()

const disposisiList = ref([])
const loading = ref(true)
const errorMessage = ref('')
const updatingId = ref(null)

const STATUS_OPTIONS = ['Belum Dibaca', 'Dibaca', 'Diproses', 'Selesai']

onMounted(loadDisposisi)

async function loadDisposisi() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await getDisposisi()
    disposisiList.value = res.data
  } catch (err) {
    if (err.response?.status === 401) { localStorage.removeItem('token'); router.push({ name: 'login' }) }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data disposisi.'
  } finally {
    loading.value = false
  }
}

async function changeStatus(d, newStatus) {
  updatingId.value = d.id
  try {
    await updateDisposisi(d.id, { status: newStatus })
    await loadDisposisi()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengubah status disposisi.')
  } finally {
    updatingId.value = null
  }
}

function statusClass(s) {
  const map = {
    'Belum Dibaca': 'badge-status draft',
    'Dibaca': 'badge-status verified',
    'Diproses': 'badge-status proses',
    'Selesai': 'badge-status selesai',
  }
  return map[s] || 'badge-status'
}

function formatDateTime(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('id-ID', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Disposisi</h2>
        <p class="greeting">Pantau dan kelola seluruh disposisi surat.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>No.</th>
            <th>Surat ID</th>
            <th>Dari</th>
            <th>Kepada</th>
            <th>Catatan</th>
            <th>Deadline</th>
            <th>Status</th>
            <th>Ubah Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(d, idx) in disposisiList" :key="d.id">
            <td>{{ idx + 1 }}</td>
            <td>#{{ d.surat_id }}</td>
            <td>{{ d.dari_user_info?.nama_lengkap || '-' }}</td>
            <td>{{ d.kepada_user_info?.nama_lengkap || '-' }}</td>
            <td class="td-perihal">{{ d.catatan || '-' }}</td>
            <td>{{ formatDateTime(d.deadline) }}</td>
            <td><span :class="statusClass(d.status)">{{ d.status }}</span></td>
            <td>
              <select
                :value="d.status"
                :disabled="updatingId === d.id"
                class="status-select"
                @change="changeStatus(d, $event.target.value)"
              >
                <option v-for="s in STATUS_OPTIONS" :key="s" :value="s">{{ s }}</option>
              </select>
            </td>
          </tr>
          <tr v-if="disposisiList.length === 0">
            <td colspan="8" class="empty-row">Belum ada disposisi.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>
  </div>
</template>
