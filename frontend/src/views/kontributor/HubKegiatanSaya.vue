<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const items = ref([])

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

const uploads = ref({})

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/kontributor/hub-kegiatan/saya')
    items.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat postingan.'
  } finally {
    loading.value = false
  }
}

function canEdit(item) {
  return item.status === 'pending'
}

async function uploadMedia(item) {
  const file = uploads.value[item.id]?.[0]
  if (!file) return
  try {
    const tipe = file.type.startsWith('video/') ? 'video' : 'foto'
    const fd = new FormData()
    fd.append('file', file)
    await api.post(`/kontributor/hub-kegiatan/${item.id}/media?tipe=${tipe}`, fd)
    uploads.value[item.id] = []
    await loadItems()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengunggah media.'
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

function mediaUrl(url) {
  return `http://localhost:8000${url}`
}
</script>

<template>
  <div class="kontributor-page">
    <h1 class="page-title">Postingan Saya</h1>
    <p class="page-subtitle">
      Postingan berstatus <strong>Menunggu</strong> masih bisa diedit dan dilengkapi media.
    </p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="text-muted">Memuat...</div>
    <div v-else-if="!items.length" class="text-muted">Belum ada postingan.</div>

    <div v-else class="list-stack">
      <div v-for="item in items" :key="item.id" class="card hub-card">
        <div class="hub-card-top">
          <span class="badge-status" :class="item.status">{{ statusLabels[item.status] }}</span>
          <span class="badge-status neutral">{{ kategoriLabels[item.kategori] }}</span>
          <span class="text-muted">{{ formatDate(item.tanggal_kegiatan) }}</span>
        </div>
        <h3 class="card-title">{{ item.judul }}</h3>
        <p class="text-muted">{{ item.deskripsi }}</p>
        <div v-if="item.catatan_moderasi" class="alert-error">
          Catatan admin: {{ item.catatan_moderasi }}
        </div>
        <div v-if="item.media?.length" class="hub-thumbs">
          <video
            v-for="m in item.media.filter((x) => x.tipe === 'video')"
            :key="m.id"
            :src="mediaUrl(m.file_url)"
            controls
            class="hub-thumb"
          ></video>
          <img
            v-for="m in item.media.filter((x) => x.tipe === 'foto')"
            :key="m.id"
            :src="mediaUrl(m.file_url)"
            alt="media"
            class="hub-thumb"
          />
        </div>
        <div v-if="canEdit(item)" class="action-row">
          <router-link :to="{ name: 'kontributor-tulis', query: { edit: item.id } }" class="btn-outline">
            Edit
          </router-link>
          <input
            type="file"
            accept="image/*,video/*"
            :ref="(el) => {}"
            @change="uploads[item.id] = [...$event.target.files]"
          />
          <button class="btn-submit" type="button" @click="uploadMedia(item)">Tambah Media</button>
        </div>
      </div>
    </div>
  </div>
</template>
