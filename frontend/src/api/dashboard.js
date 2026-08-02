/**
 * Dashboard API module
 * Centralizes all dashboard-related API calls used by the dashboard store.
 */
import api from './axios'

/** Task 6.2 — Statistik API */
export function fetchStatistikAPI() {
  return api.get('/dashboard/statistik')
}

/** Task 6.3 — Grafik API */
export function fetchGrafikAPI() {
  return api.get('/dashboard/grafik')
}

/** Task 6.4 — Perbandingan API */
export function fetchPerbandinganAPI() {
  return api.get('/dashboard/perbandingan')
}

/** Convenience: fetch all three in parallel */
export function fetchAllDashboard() {
  return Promise.all([
    fetchStatistikAPI(),
    fetchGrafikAPI(),
    fetchPerbandinganAPI()
  ])
}
