<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const items = ref([])
const activeTab = ref('pending')

const kategoriLabels = {
  berita: 'Berita',
  dokumentasi: 'Dokumentasi',
  agenda: 'Agenda'
}
const statusLabels = {
  pending: 'Menunggu',
  approved: 'Disetujui',
  rejected: 'Ditolak'
}
const tingkatLabels = {
  kwarcab: 'Kwarcab',
  kwaran: 'Kwaran',
  gudep: 'Gudep'
}

const showReject = ref(false)
const rejectItem = ref(null)
const rejectNote = ref('')

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/hub-kegiatan')
    items.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
}

function filtered() {
  return items.value.filter((h) => h.status === activeTab.value)
}

async function approve(item) {
  try {
    await api.patch(`/admin/hub-kegiatan/${item.id}/approve`)
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyetujui.'
  }
}

function openReject(item) {
  rejectItem.value = item
  rejectNote.value = ''
  showReject.value = true
}

async function confirmReject() {
  if (!rejectNote.value.trim()) return
  try {
    await api.patch(`/admin/hub-kegiatan/${rejectItem.value.id}/reject`, {
      catatan_moderasi: rejectNote.value.trim()
    })
    showReject.value = false
    rejectItem.value = null
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menolak.'
  }
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso + 'T00:00:00').toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

function goToDetail(item) {
  router.push({ name: 'hub-kegiatan-detail', params: { id: item.id } })
}
</script>

<template>
  <div class="page">
    <h1 class="page-title">Moderasi Postingan Hub</h1>
    <p class="page-subtitle">
      Postingan dari kontributor (Kwarcab / Kwaran / Gudep) harus disetujui sebelum tampil di publik.
    </p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="tabs">
      <button
        v-for="tab in ['pending', 'approved', 'rejected']"
        :key="tab"
        class="tab-btn"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ statusLabels[tab] }}
        <span class="tab-count">{{ items.filter((h) => h.status === tab).length }}</span>
      </button>
    </div>

    <div v-if="loading" class="text-muted">Memuat...</div>
    <div v-else-if="!filtered().length" class="text-muted">Tidak ada postingan pada tab ini.</div>

    <div v-else class="list-stack">
      <div v-for="item in filtered()" :key="item.id" class="card hub-card">
        <div class="hub-card-top">
          <span class="badge-status" :class="item.status">{{ statusLabels[item.status] }}</span>
          <span class="badge-status neutral">{{ kategoriLabels[item.kategori] }}</span>
          <span class="badge-status neutral">{{ tingkatLabels[item.tingkat_wilayah] }} {{ item.nama_wilayah }}</span>
          <span class="text-muted">{{ formatDate(item.tanggal_kegiatan) }}</span>
        </div>
        <h3 class="card-title">{{ item.judul }}</h3>
        <p class="text-muted">{{ item.deskripsi }}</p>
        <p class="text-muted small">
          Lokasi: {{ item.lokasi || '-' }} | Media: {{ item.media?.length || 0 }}
        </p>
        <p v-if="item.status === 'rejected' && item.catatan_moderasi" class="alert-error">
          Catatan: {{ item.catatan_moderasi }}
        </p>
        <div class="action-row">
          <button class="btn-outline" type="button" @click="goToDetail(item)">Detail</button>
          <template v-if="item.status === 'pending'">
            <button class="btn-submit" type="button" @click="approve(item)">Setujui</button>
            <button class="btn-danger" type="button" @click="openReject(item)">Tolak</button>
          </template>
        </div>
      </div>
    </div>

    <div v-if="showReject" class="modal-overlay" @click.self="showReject = false">
      <div class="modal-card">
        <h3 class="card-title">Tolak Postingan</h3>
        <p class="text-muted">Alasan wajib diisi dan akan ditampilkan ke kontributor.</p>
        <textarea
          v-model="rejectNote"
          rows="4"
          placeholder="Alasan penolakan..."
        ></textarea>
        <div class="action-row">
          <button class="btn-outline" type="button" @click="showReject = false">Batal</button>
          <button class="btn-danger" type="button" :disabled="!rejectNote.trim()" @click="confirmReject">
            Konfirmasi Tolak
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
