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
  <div class="page-container">
    
    <!-- Header -->
    <div class="page-header">
      <h2 class="page-title">Katalog e-Pelatihan</h2>
      <p class="page-subtitle">Tingkatkan kompetensi Pramuka Anda melalui modul pembelajaran mandiri yang interaktif.</p>
    </div>

    <!-- State: Loading -->
    <div v-if="loading" class="state-center">
      <div class="spinner"></div>
      <p class="state-text">Memuat katalog pelatihan...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="state-error">
      {{ error }}
    </div>

    <!-- State: Empty -->
    <div v-else-if="trainings.length === 0" class="state-empty">
      <div class="empty-icon">📚</div>
      <h3>Belum ada pelatihan tersedia</h3>
      <p>Silakan kembali lagi nanti saat admin sudah mempublikasikan modul baru.</p>
    </div>
    
    <!-- Content: Grid -->
    <div v-else class="card-grid">
      <div v-for="(training, index) in trainings" :key="training.id" 
           class="training-card"
           :style="`animation-delay: ${index * 0.08}s`">
        
        <div class="card-badge">LMS PROGRAM</div>
        
        <h3 class="card-title">{{ training.title }}</h3>
        
        <p class="card-desc">
          {{ training.description || 'Pelatihan ini tidak memiliki deskripsi khusus. Silakan masuk untuk melihat detail modul.' }}
        </p>
        
        <div class="card-meta">
          <div class="meta-row">
            <span class="meta-label">Mulai</span>
            <span class="meta-value">{{ formatDate(training.start_date) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">KKM</span>
            <span class="meta-value">{{ training.passing_grade }} Poin</span>
          </div>
        </div>
        
        <router-link :to="{ name: 'lms-training-detail', params: { id: training.id } }" class="card-btn">
          Lihat Detail Modul &rarr;
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  min-height: 80vh;
}

/* Header */
.page-header {
  margin-bottom: 2.5rem;
  animation: fadeDown 0.5s ease-out;
}
.page-title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 800;
  background: linear-gradient(135deg, var(--brown), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}
.page-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
}

/* States */
.state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 2rem;
}
.state-text { color: #6b7280; font-weight: 500; }
.spinner {
  width: 52px;
  height: 52px;
  border: 4px solid #e5e7eb;
  border-top-color: var(--gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.state-error {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
}
.state-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 24px;
  border: 2px dashed #e5e7eb;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.state-empty h3 { font-size: 1.25rem; font-weight: 700; color: #374151; margin-bottom: 0.5rem; }
.state-empty p { color: #9ca3af; }

/* Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Card */
.training-card {
  background: white;
  border-radius: 20px;
  padding: 1.75rem;
  border: 1px solid #f0ebe4;
  box-shadow: 0 4px 20px rgba(92, 64, 51, 0.06);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  animation: fadeUp 0.4s ease-out both;
  position: relative;
  overflow: hidden;
}
.training-card::before {
  content: '';
  position: absolute;
  top: -40px;
  right: -40px;
  width: 120px;
  height: 120px;
  background: radial-gradient(circle, rgba(212, 172, 13, 0.12) 0%, transparent 70%);
  border-radius: 50%;
  transition: transform 0.4s ease;
}
.training-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(92, 64, 51, 0.14);
}
.training-card:hover::before {
  transform: scale(1.6);
}

.card-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  background: #faf6f0;
  color: var(--brown);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  border-radius: 999px;
  width: fit-content;
  border: 1px solid rgba(92, 64, 51, 0.12);
}

.card-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.4;
  margin: 0.25rem 0;
  transition: color 0.2s;
}
.training-card:hover .card-title {
  color: var(--maroon);
}

.card-desc {
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  background: #fafafa;
  border: 1px solid #f0ebe4;
  border-radius: 12px;
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 0.25rem 0;
}
.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.825rem;
}
.meta-label {
  color: var(--gold);
  font-weight: 600;
}
.meta-value {
  color: #374151;
  font-weight: 600;
}

.card-btn {
  display: block;
  text-align: center;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, var(--brown), var(--brown-dark));
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 12px;
  text-decoration: none;
  transition: all 0.2s ease;
  margin-top: auto;
}
.card-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(92, 64, 51, 0.3);
}
.card-btn:active {
  transform: translateY(0);
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .page-container { padding: 1.25rem 1rem; }
  .card-grid { grid-template-columns: 1fr; }
}
</style>
