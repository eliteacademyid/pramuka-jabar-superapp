/**
 * useDashboard — composable for dashboard data management.
 * Provides a clean interface for dashboard pages to consume store data,
 * with built-in retry logic and state accessors.
 * Task 8.3 — verify dashboard functionality.
 */
import { computed, onMounted } from 'vue'
import { useDashboardStore } from '../store/dashboard'
import { useGlobalStore } from '../store/global'
import { extractErrorMessage } from './errorHandler'

export function useDashboard() {
  const dashboardStore = useDashboardStore()
  const globalStore = useGlobalStore()

  // ── Computed state ────────────────────────────────────────────────────────
  const isLoading = computed(() => dashboardStore.loading)
  const hasError = computed(() => Boolean(dashboardStore.error))
  const errorMessage = computed(() => dashboardStore.error)

  const statistik = computed(() => dashboardStore.statistik)
  const grafik = computed(() => dashboardStore.grafik)
  const perbandingan = computed(() => dashboardStore.perbandingan)

  // Derived stat values with safe fallbacks
  const statValues = computed(() => ({
    totalProgram: statistik.value.total_program ?? 0,
    totalKegiatan: statistik.value.total_kegiatan ?? 0,
    programBerjalan: statistik.value.program_berjalan ?? 0,
    programSelesai: statistik.value.program_selesai ?? 0,
    menungguApproval: statistik.value.menunggu_approval ?? 0,
    totalAnggaran: statistik.value.total_anggaran ?? 0,
    realisasiAnggaran: statistik.value.realisasi_anggaran ?? 0,
    persentaseCapaian: statistik.value.persentase_capaian ?? '0%'
  }))

  // ── Actions ───────────────────────────────────────────────────────────────

  async function loadAll() {
    try {
      globalStore.startLoading('Memuat dashboard...')
      await dashboardStore.getDashboard()
    } catch (err) {
      globalStore.toast.error(extractErrorMessage(err, 'Gagal memuat dashboard.'))
    } finally {
      globalStore.stopLoading()
    }
  }

  async function retry() {
    dashboardStore.reset()
    await loadAll()
  }

  // Auto-load on component mount
  onMounted(loadAll)

  return {
    isLoading,
    hasError,
    errorMessage,
    statistik,
    grafik,
    perbandingan,
    statValues,
    loadAll,
    retry
  }
}
