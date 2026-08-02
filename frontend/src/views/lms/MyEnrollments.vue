<script setup>
import { ref, onMounted } from 'vue'
import lmsService from '../../services/lms'

const enrollments = ref([])
const trainings = ref({})
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const eRes = await lmsService.getMyEnrollments()
    enrollments.value = eRes.data

    if (enrollments.value.length > 0) {
      const tRes = await lmsService.getTrainings({ limit: 50 })
      const allTrainings = tRes.data.items || tRes.data
      allTrainings.forEach(t => {
        trainings.value[t.id] = t
      })
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Gagal memuat riwayat pelatihan'
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
      <h2 class="page-title">Riwayat Pelatihanku</h2>
      <p class="page-subtitle">Pantau progres belajar dan unduh sertifikat kelulusan Anda di sini.</p>
    </div>

    <!-- State: Loading -->
    <div v-if="loading" class="state-center">
      <div class="spinner"></div>
      <p class="state-text">Memuat data riwayat...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="state-error">
      {{ error }}
    </div>

    <!-- State: Empty -->
    <div v-else-if="enrollments.length === 0" class="state-empty">
      <div class="empty-icon">📖</div>
      <h3>Anda belum mengikuti pelatihan</h3>
      <p>Jelajahi katalog pelatihan dan mulai tingkatkan kemampuan Anda.</p>
      <router-link to="/admin/trainings" class="empty-btn">
        Lihat Katalog Pelatihan
      </router-link>
    </div>

    <!-- Content -->
    <div v-else class="card-grid">
      <div v-for="(e, index) in enrollments" :key="e.id"
           class="enroll-card"
           :style="`animation-delay: ${index * 0.08}s`">

        <!-- Top row: status badge -->
        <div class="card-top">
          <span :class="['status-badge', 
            e.status === 'Lulus' ? 'badge-lulus' : 
            e.status === 'Gagal' ? 'badge-gagal' : 'badge-proses']">
            {{ e.status === 'Lulus' ? 'Lulus' : e.status === 'Gagal' ? 'Tidak Lulus' : 'Sedang Belajar' }}
          </span>
          <span class="enroll-date">{{ formatDate(e.enrolled_at) }}</span>
        </div>

        <!-- Title -->
        <h3 class="card-title">
          {{ trainings[e.training_id]?.title || 'Memuat...' }}
        </h3>

        <!-- Progress -->
        <div class="progress-section">
          <div class="progress-header">
            <span class="progress-label">Progres</span>
            <span :class="['progress-pct', e.progress_percentage >= 100 ? 'pct-done' : '']">
              {{ e.progress_percentage }}%
            </span>
          </div>
          <div class="progress-track">
            <div class="progress-fill"
                 :class="e.progress_percentage >= 100 ? 'fill-done' : 'fill-active'"
                 :style="{ width: `${e.progress_percentage}%` }">
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <router-link :to="{ name: 'lms-training-detail', params: { id: e.training_id } }"
                       class="btn-secondary">
            Lanjut Belajar
          </router-link>
          <router-link v-if="e.status === 'Lulus'"
                       :to="`/admin/enrollments/${e.id}/certificate`"
                       class="btn-cert">
            Sertifikat
          </router-link>
        </div>
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
  gap: 0.75rem;
}
.empty-icon { font-size: 3rem; }
.state-empty h3 { font-size: 1.25rem; font-weight: 700; color: #374151; }
.state-empty p { color: #9ca3af; }
.empty-btn {
  display: inline-block;
  margin-top: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--maroon);
  color: white;
  font-weight: 600;
  border-radius: 10px;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.empty-btn:hover { background: var(--maroon-dark); }

/* Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* Enrollment Card */
.enroll-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid #f0ebe4;
  box-shadow: 0 4px 20px rgba(92, 64, 51, 0.06);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  animation: fadeUp 0.4s ease-out both;
}
.enroll-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(92, 64, 51, 0.12);
}

/* Card Top */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}
.status-badge {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.badge-lulus {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
}
.badge-gagal {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}
.badge-proses {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}
.enroll-date {
  font-size: 0.75rem;
  color: #9ca3af;
  white-space: nowrap;
}

/* Card Title */
.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.4;
  margin: 0;
}

/* Progress */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.progress-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #6b7280;
}
.progress-pct {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--brown);
}
.pct-done { color: #16a34a; }
.progress-track {
  width: 100%;
  height: 10px;
  background: #f3f4f6;
  border-radius: 999px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.08);
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 1s ease;
}
.fill-active {
  background: linear-gradient(90deg, var(--gold), var(--brown));
}
.fill-done {
  background: linear-gradient(90deg, #4ade80, #16a34a);
}

/* Actions */
.card-actions {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-top: auto;
}
.btn-secondary {
  display: block;
  text-align: center;
  padding: 0.7rem 1rem;
  background: #1f2937;
  color: white;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}
.btn-secondary:hover {
  background: #111827;
  transform: translateY(-1px);
}
.btn-cert {
  display: block;
  text-align: center;
  padding: 0.7rem 1rem;
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: white;
  font-size: 0.875rem;
  font-weight: 700;
  border-radius: 10px;
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(22, 163, 74, 0.25);
  transition: all 0.2s ease;
}
.btn-cert:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(22, 163, 74, 0.35);
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
