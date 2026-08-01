<script setup>
import { ref, onMounted } from 'vue'
import lmsService from '../../services/lms'

const trainings = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await lmsService.getTrainings()
    trainings.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Gagal memuat daftar pelatihan'
  } finally {
    loading.value = false
  }
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <h2>Daftar Pelatihan</h2>
    </div>

    <div v-if="loading" class="empty-row">
      Memuat data pelatihan...
    </div>
    <div v-else-if="error" class="alert-error">
      {{ error }}
    </div>
    <div v-else-if="trainings.length === 0" class="empty-row">
      Belum ada pelatihan yang tersedia saat ini.
    </div>
    
    <div v-else class="card-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
      <div v-for="training in trainings" :key="training.id" class="stat-card" style="align-items: flex-start;">
        <h3 style="color: var(--brown); margin-bottom: 0.5rem; font-size: 1.25rem;">{{ training.title }}</h3>
        <p style="font-size: 0.85rem; color: #8a7a6d; margin-bottom: 1rem; line-height: 1.4;">
          {{ training.description || 'Tidak ada deskripsi.' }}
        </p>
        <div style="font-size: 0.85rem; margin-bottom: 1rem; flex: 1;">
          <div><strong>Mulai:</strong> {{ formatDate(training.start_date) }}</div>
          <div><strong>Selesai:</strong> {{ formatDate(training.end_date) }}</div>
          <div><strong>Passing Grade:</strong> {{ training.passing_grade }}</div>
        </div>
        <router-link :to="{ name: 'lms-training-detail', params: { id: training.id } }" class="btn-primary" style="width: 100%; text-align: center; padding: 0.6rem;">
          Lihat Detail
        </router-link>
      </div>
    </div>
  </div>
</template>
