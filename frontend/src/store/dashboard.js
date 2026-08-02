import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchStatistikAPI, fetchGrafikAPI, fetchPerbandinganAPI } from '../api/dashboard'
import { extractErrorMessage, logError } from '../utils/errorHandler'

/**
 * Dashboard store — manages statistik, grafik, and perbandingan data
 * fetched from the backend API with integrated loading and error state.
 */
export const useDashboardStore = defineStore('dashboard', () => {
  // ── State ────────────────────────────────────────────────────────────────
  const statistik = ref({})
  const grafik = ref({})
  const perbandingan = ref([])

  // Task 6.5 — granular loading state per endpoint + global
  const loading = ref(false)
  const loadingStatistik = ref(false)
  const loadingGrafik = ref(false)
  const loadingPerbandingan = ref(false)

  /** Computed helper: any endpoint is still loading */
  const isAnyLoading = computed(
    () => loading.value || loadingStatistik.value || loadingGrafik.value || loadingPerbandingan.value
  )

  // Task 6.6 — error handling state
  const error = ref('')
  const errorStatistik = ref('')
  const errorGrafik = ref('')
  const errorPerbandingan = ref('')

  // ── Actions ──────────────────────────────────────────────────────────────

  /** Task 6.2 — Fetch all dashboard data in parallel */
  async function getDashboard() {
    loading.value = true
    error.value = ''
    try {
      await Promise.all([
        fetchStatistik(),
        fetchGrafik(),
        fetchPerbandingan()
      ])
    } catch (err) {
      logError('getDashboard', err)
      error.value = extractErrorMessage(err, 'Gagal memuat data dashboard.')
    } finally {
      loading.value = false
    }
  }

  /** Task 6.2 — Statistik API integration */
  async function getStatistik() {
    loadingStatistik.value = true
    errorStatistik.value = ''
    try {
      await fetchStatistik()
    } catch (err) {
      logError('getStatistik', err)
      errorStatistik.value = extractErrorMessage(err, 'Gagal memuat statistik.')
      throw err
    } finally {
      loadingStatistik.value = false
    }
  }

  async function fetchStatistik() {
    const response = await fetchStatistikAPI()
    statistik.value = response.data
    return response.data
  }

  /** Task 6.3 — Grafik API integration */
  async function getGrafik() {
    loadingGrafik.value = true
    errorGrafik.value = ''
    try {
      await fetchGrafik()
    } catch (err) {
      logError('getGrafik', err)
      errorGrafik.value = extractErrorMessage(err, 'Gagal memuat data grafik.')
      throw err
    } finally {
      loadingGrafik.value = false
    }
  }

  async function fetchGrafik() {
    const response = await fetchGrafikAPI()
    grafik.value = response.data
    return response.data
  }

  /** Task 6.4 — Perbandingan API integration */
  async function getPerbandingan() {
    loadingPerbandingan.value = true
    errorPerbandingan.value = ''
    try {
      await fetchPerbandingan()
    } catch (err) {
      logError('getPerbandingan', err)
      errorPerbandingan.value = extractErrorMessage(err, 'Gagal memuat data perbandingan.')
      throw err
    } finally {
      loadingPerbandingan.value = false
    }
  }

  async function fetchPerbandingan() {
    const response = await fetchPerbandinganAPI()
    perbandingan.value = response.data
    return response.data
  }

  /** Reset all state */
  function reset() {
    statistik.value = {}
    grafik.value = {}
    perbandingan.value = []
    error.value = ''
    errorStatistik.value = ''
    errorGrafik.value = ''
    errorPerbandingan.value = ''
  }

  return {
    // state
    statistik,
    grafik,
    perbandingan,
    loading,
    loadingStatistik,
    loadingGrafik,
    loadingPerbandingan,
    isAnyLoading,
    error,
    errorStatistik,
    errorGrafik,
    errorPerbandingan,
    // actions
    getDashboard,
    getStatistik,
    getGrafik,
    getPerbandingan,
    reset
  }
})
