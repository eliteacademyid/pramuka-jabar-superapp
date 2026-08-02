<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const items = ref([])
const total = ref(0)

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

const filters = reactive({
  kategori: '',
  tingkat_wilayah: '',
  q: ''
})

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (filters.kategori) params.kategori = filters.kategori
    if (filters.tingkat_wilayah) params.tingkat_wilayah = filters.tingkat_wilayah
    if (filters.q.trim()) params.q = filters.q.trim()
    const res = await api.get('/public/hub-kegiatan', { params })
    items.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso + 'T00:00:00').toLocaleDateString('id-ID', {
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
    <h1 class="page-title">Hub Kegiatan</h1>
    <p class="page-subtitle">
      Kegiatan dan informasi terbaru dari Kwarcab, Kwaran, dan Gugus Depan se-Jawa Barat.
    </p>

    <div class="filters-bar">
      <select v-model="filters.kategori" @change="loadItems">
        <option value="">Semua Kategori</option>
        <option value="berita">Berita</option>
        <option value="dokumentasi">Dokumentasi</option>
        <option value="agenda">Agenda</option>
      </select>
      <select v-model="filters.tingkat_wilayah" @change="loadItems">
        <option value="">Semua Tingkat</option>
        <option value="kwarcab">Kwarcab</option>
        <option value="kwaran">Kwaran</option>
        <option value="gudep">Gudep</option>
      </select>
      <input
        v-model="filters.q"
        type="text"
        placeholder="Cari judul / lokasi..."
        @keyup.enter="loadItems"
      />
      <button class="btn-outline" type="button" @click="loadItems">Cari</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="text-muted">Memuat...</div>
    <div v-else-if="!items.length" class="text-muted">Belum ada postingan yang disetujui.</div>

    <div v-else class="list-stack">
      <router-link
        v-for="item in items"
        :key="item.id"
        :to="{ name: 'hub-kegiatan-detail', params: { id: item.id } }"
        class="card hub-card public-card"
      >
        <div class="hub-card-top">
          <span class="badge-status neutral">{{ kategoriLabels[item.kategori] }}</span>
          <span class="badge-status neutral">{{ tingkatLabels[item.tingkat_wilayah] }} {{ item.nama_wilayah }}</span>
          <span class="text-muted">{{ formatDate(item.tanggal_kegiatan) }}</span>
        </div>
        <h3 class="card-title">{{ item.judul }}</h3>
        <p class="text-muted">{{ item.deskripsi }}</p>
        <div v-if="item.media?.length" class="hub-thumbs">
          <img
            v-for="m in item.media.filter((x) => x.tipe === 'foto').slice(0, 3)"
            :key="m.id"
            :src="mediaUrl(m.file_url)"
            alt="media"
            class="hub-thumb"
          />
        </div>
      </router-link>
    </div>

    <p v-if="total" class="text-muted small">Total {{ total }} postingan.</p>
  </div>
</template>
