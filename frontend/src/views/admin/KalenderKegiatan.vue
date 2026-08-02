<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const items = ref([])

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth())

const showDetail = ref(false)
const detailItem = ref(null)

const namaBulan = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]
const namaHari = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab']

const statusColors = {
  rencana: 'var(--gold)',
  berjalan: '#2ecc71',
  selesai: '#3498db',
  dibatalkan: '#e74c3c'
}

onMounted(loadItems)

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/kegiatan')
    items.value = res.data
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
      return
    }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat kegiatan.'
  } finally {
    loading.value = false
  }
}

function hariDalamBulan(y, m) {
  return new Date(y, m + 1, 0).getDate()
}

const cells = computed(() => {
  const y = year.value
  const m = month.value
  const total = hariDalamBulan(y, m)
  const offset = new Date(y, m, 1).getDay()

  const byDate = {}
  for (const k of items.value) {
    const start = new Date(k.tanggal_mulai + 'T00:00:00')
    let end = k.tanggal_selesai ? new Date(k.tanggal_selesai + 'T00:00:00') : start
    if (end < start) end = start
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      if (!byDate[key]) byDate[key] = []
      byDate[key].push(k)
    }
  }

  const result = []
  for (let i = 0; i < offset; i++) {
    result.push({ blank: true })
  }
  for (let day = 1; day <= total; day++) {
    const key = `${y}-${String(m + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const today = new Date()
    const isToday =
      today.getFullYear() === y && today.getMonth() === m && today.getDate() === day
    result.push({
      day,
      key,
      isToday,
      kegiatan: byDate[key] || []
    })
  }
  return result
})

function prevMonth() {
  month.value -= 1
  if (month.value < 0) {
    month.value = 11
    year.value -= 1
  }
}

function nextMonth() {
  month.value += 1
  if (month.value > 11) {
    month.value = 0
    year.value += 1
  }
}

function today() {
  const t = new Date()
  year.value = t.getFullYear()
  month.value = t.getMonth()
}

function openDetail(item) {
  detailItem.value = item
  showDetail.value = true
}

function statusBadge(s) {
  return `badge badge-status-${s}`
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Kalender Kegiatan</h2>
        <p class="greeting">Agenda kegiatan Kwarda dalam tampilan kalender bulanan.</p>
      </div>
      <button class="btn-primary btn-add" @click="today">Hari Ini</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="calendar-card" v-if="!loading">
      <div class="calendar-header">
        <button class="btn-small" @click="prevMonth">&laquo; Bulan Sebelumnya</button>
        <div class="calendar-title">
          {{ namaBulan[month] }} {{ year }}
        </div>
        <button class="btn-small" @click="nextMonth">Bulan Berikutnya &raquo;</button>
      </div>

      <div class="calendar-grid calendar-weekdays">
        <div v-for="h in namaHari" :key="h" class="calendar-day head">{{ h }}</div>
      </div>
      <div class="calendar-grid">
        <div
          v-for="(cell, idx) in cells"
          :key="idx"
          class="calendar-day"
          :class="{ blank: cell.blank, today: cell.isToday }"
        >
          <template v-if="!cell.blank">
            <div class="calendar-date">{{ cell.day }}</div>
            <button
              v-for="k in cell.kegiatan.slice(0, 3)"
              :key="k.id"
              class="calendar-chip"
              :style="{ borderLeftColor: statusColors[k.status] }"
              @click="openDetail(k)"
              :title="k.judul"
            >
              {{ k.judul }}
            </button>
            <span v-if="cell.kegiatan.length > 3" class="calendar-more">
              +{{ cell.kegiatan.length - 3 }} lainnya
            </span>
          </template>
        </div>
      </div>

      <div class="calendar-legend">
        <span v-for="(color, s) in statusColors" :key="s" class="legend-item">
          <i class="legend-dot" :style="{ backgroundColor: color }"></i>{{ s }}
        </span>
      </div>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showDetail" class="modal-overlay" @click.self="showDetail = false">
      <div class="modal-card detail-card">
        <h3>{{ detailItem.judul }}</h3>
        <p class="greeting">
          {{ detailItem.tanggal_mulai }} — {{ detailItem.lokasi || 'lokasi belum diisi' }}
        </p>
        <p><span :class="statusBadge(detailItem.status)">{{ detailItem.status }}</span></p>
        <p>{{ detailItem.deskripsi || '-' }}</p>
        <p v-if="detailItem.penanggung_jawab">
          PJ: <strong>{{ detailItem.penanggung_jawab }}</strong>
        </p>
        <div class="modal-actions">
          <button class="btn-small" @click="showDetail = false">Tutup</button>
          <router-link
            class="btn-small"
            :to="{ name: 'admin-kegiatan' }"
            @click="showDetail = false"
          >Kelola di Kegiatan &amp; Jadwal</router-link>
        </div>
      </div>
    </div>
  </div>
</template>
