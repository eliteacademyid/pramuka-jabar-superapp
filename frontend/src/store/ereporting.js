import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/axios'

export const useEReportingStore = defineStore('ereporting', () => {
  // ─── Realisasi ────────────────────────────────────────────────
  const realisasiList = ref([])
  const realisasiLoading = ref(false)

  async function fetchRealisasi(params = {}) {
    realisasiLoading.value = true
    try {
      const res = await api.get('/realisasi', { params })
      realisasiList.value = res.data
      return res.data
    } finally {
      realisasiLoading.value = false
    }
  }

  async function createRealisasi(payload) {
    const res = await api.post('/realisasi', payload)
    return res.data
  }

  // Upload file — returns { filename, url, message }
  async function uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res.data
  }

  // ─── Laporan ──────────────────────────────────────────────────
  const laporanList = ref([])
  const laporanLoading = ref(false)

  async function fetchLaporan(params = {}) {
    laporanLoading.value = true
    try {
      const res = await api.get('/laporan', { params })
      laporanList.value = res.data
      return res.data
    } finally {
      laporanLoading.value = false
    }
  }

  async function createLaporan(payload) {
    const res = await api.post('/laporan', payload)
    return res.data
  }

  // ─── Approval ─────────────────────────────────────────────────
  async function processApproval(payload) {
    // payload: { laporan_id, status: 'approved'|'rejected', catatan? }
    const res = await api.post('/approval', payload)
    return res.data
  }

  // ─── Dashboard ────────────────────────────────────────────────
  const statistik = ref(null)
  const grafik = ref([])
  const perbandingan = ref(null)
  const dashboardLoading = ref(false)

  async function fetchDashboard() {
    dashboardLoading.value = true
    try {
      const [s, g, p] = await Promise.all([
        api.get('/dashboard/statistik'),
        api.get('/dashboard/grafik'),
        api.get('/dashboard/perbandingan')
      ])
      statistik.value = s.data
      grafik.value = g.data
      perbandingan.value = p.data
    } finally {
      dashboardLoading.value = false
    }
  }

  return {
    // realisasi
    realisasiList, realisasiLoading, fetchRealisasi, createRealisasi, uploadFile,
    // laporan
    laporanList, laporanLoading, fetchLaporan, createLaporan,
    // approval
    processApproval,
    // dashboard
    statistik, grafik, perbandingan, dashboardLoading, fetchDashboard
  }
})
