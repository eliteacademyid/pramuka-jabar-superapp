import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/axios'

export const useDashboardStore = defineStore('dashboard', () => {
  const statistik = ref({})
  const grafik = ref({})
  const perbandingan = ref([])
  const loading = ref(false)

  async function getDashboard() {
    loading.value = true
    try {
      const [stat, graph, compare] = await Promise.all([
        getStatistik(),
        getGrafik(),
        getPerbandingan()
      ])
      return { stat, graph, compare }
    } finally {
      loading.value = false
    }
  }

  async function getStatistik() {
    const response = await api.get('/dashboard/statistik')
    statistik.value = response.data
    return response.data
  }

  async function getGrafik() {
    const response = await api.get('/dashboard/grafik')
    grafik.value = response.data
    return response.data
  }

  async function getPerbandingan() {
    const response = await api.get('/dashboard/perbandingan')
    perbandingan.value = response.data
    return response.data
  }

  return { statistik, grafik, perbandingan, loading, getDashboard, getStatistik, getGrafik, getPerbandingan }
})
