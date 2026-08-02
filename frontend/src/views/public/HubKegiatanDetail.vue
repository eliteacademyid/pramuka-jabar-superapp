<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const item = ref(null)

const kategoriLabels = {
  berita: 'Berita',
  dokumentasi: 'Dokumentasi',
  agenda: 'Agenda'
}
const tingkatLabels = {
  kwarcab: 'Kwarcab',
  kwaran: 'Kwaran',
  gudep: 'Gudep'
}

onMounted(loadItem)

async function loadItem() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get(`/public/hub-kegiatan/${route.params.id}`)
    item.value = res.data
  } catch (err) {
    errorMessage.value =
      err.response?.status === 404
        ? 'Postingan tidak ditemukan atau belum disetujui.'
        : err.response?.data?.detail || 'Gagal memuat detail.'
  } finally {
    loading.value = false
  }
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso + 'T00:00:00').toLocaleDateString('id-ID', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function mediaUrl(url) {
  return `http://localhost:8000${url}`
}
</script>

<template>
  <div class="page">
    <router-link to="/hub-kegiatan" class="back-link">Kembali ke Hub Kegiatan</router-link>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="text-muted">Memuat...</div>

    <article v-else-if="item" class="card hub-card detail-card">
      <div class="hub-card-top">
        <span class="badge-status neutral">{{ kategoriLabels[item.kategori] }}</span>
        <span class="badge-status neutral">{{ tingkatLabels[item.tingkat_wilayah] }} {{ item.nama_wilayah }}</span>
        <span class="text-muted">{{ formatDate(item.tanggal_kegiatan) }}</span>
      </div>
      <h1 class="page-title">{{ item.judul }}</h1>
      <p class="text-muted">Lokasi: {{ item.lokasi || '-' }} | Dibuat: {{ new Date(item.created_at).toLocaleString('id-ID') }}</p>

      <p class="hub-deskripsi">{{ item.deskripsi }}</p>

      <div v-if="item.media?.length" class="hub-gallery">
        <video
          v-for="m in item.media.filter((x) => x.tipe === 'video')"
          :key="m.id"
          :src="mediaUrl(m.file_url)"
          controls
          class="hub-media"
        ></video>
        <img
          v-for="m in item.media.filter((x) => x.tipe === 'foto')"
          :key="m.id"
          :src="mediaUrl(m.file_url)"
          :alt="item.judul"
          class="hub-media"
        />
      </div>
    </article>
  </div>
</template>
