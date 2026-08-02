<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import lmsService from '../../services/lms'
import ActionModal from '../../components/ActionModal.vue'

const route = useRoute()
const router = useRouter()
const trainingId = route.params.id

const training = ref(null)
const materials = ref([])
const isEnrolled = ref(false)
const loading = ref(true)
const enrolling = ref(false)
const error = ref('')
const hasQuiz = ref(false)
const modal = ref({ show: false, type: 'success', title: '', message: '' })

function showModal(type, title, message) {
  modal.value = { show: true, type, title, message }
}

onMounted(async () => {
  await fetchTrainingData()
})

async function fetchTrainingData() {
  loading.value = true
  error.value = ''
  try {
    const tRes = await lmsService.getTrainings()
    const allTrainings = tRes.data.items || tRes.data
    training.value = allTrainings.find(t => t.id == trainingId)

    if (!training.value) {
      error.value = 'Pelatihan tidak ditemukan'
      return
    }

    const eRes = await lmsService.getMyEnrollments()
    const enrollment = eRes.data.find(e => e.training_id == trainingId)
    isEnrolled.value = !!enrollment

    if (isEnrolled.value) {
      const mRes = await lmsService.getTrainingMaterials(trainingId)
      materials.value = mRes.data

      try {
        await lmsService.getQuiz(trainingId)
        hasQuiz.value = true
      } catch {
        hasQuiz.value = false
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Gagal memuat detail pelatihan'
  } finally {
    loading.value = false
  }
}

async function enroll() {
  enrolling.value = true
  try {
    await lmsService.enrollTraining(trainingId)
    await fetchTrainingData()
    showModal('success', 'Berhasil Mendaftar', 'Selamat! Anda berhasil mendaftar pelatihan ini. Modul pembelajaran kini dapat diakses.')
  } catch (err) {
    showModal('error', 'Gagal Mendaftar', err.response?.data?.detail || 'Gagal mendaftar pelatihan. Silakan coba lagi.')
  } finally {
    enrolling.value = false
  }
}
</script>

<template>
  <div class="page-container">

    <ActionModal
      :show="modal.show"
      :type="modal.type"
      :title="modal.title"
      :message="modal.message"
      @close="modal.show = false"
    />

    <!-- Loading -->
    <div v-if="loading" class="state-center">
      <div class="spinner"></div>
      <p class="state-text">Memuat detail pelatihan...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-error">
      {{ error }}
      <router-link to="/admin/trainings" class="back-link">Kembali ke Daftar</router-link>
    </div>

    <!-- Content -->
    <div v-else-if="training" class="content-wrap">

      <!-- Back link -->
      <router-link to="/admin/trainings" class="back-btn">
        &larr; Kembali ke Daftar
      </router-link>

      <!-- Hero Card -->
      <div class="hero-card">
        <div class="hero-deco"></div>
        <div class="hero-body">
          <div class="hero-left">
            <span :class="['status-pill', training.status === 'Published' ? 'pill-published' : 'pill-draft']">
              {{ training.status === 'Published' ? 'Tersedia' : 'Draft' }}
            </span>
            <h2 class="hero-title">{{ training.title }}</h2>
            <p class="hero-desc">{{ training.description }}</p>
          </div>

          <!-- Enroll Box -->
          <div class="enroll-box">
            <div v-if="!isEnrolled">
              <p class="enroll-label">Siap Belajar?</p>
              <button @click="enroll" :disabled="enrolling" class="enroll-btn">
                {{ enrolling ? 'Memproses...' : 'Daftar Sekarang' }}
              </button>
            </div>
            <div v-else class="enrolled-badge">
              <div class="check-icon">&#10003;</div>
              <div>
                <p class="enrolled-text">Telah Terdaftar</p>
                <p class="enrolled-sub">Akses modul terbuka</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Materials Section -->
      <div v-if="isEnrolled" class="materials-section">
        <div class="section-header">
          <div class="section-bar"></div>
          <h3 class="section-title">Modul Pembelajaran</h3>
        </div>

        <div v-if="materials.length === 0" class="empty-materials">
          Modul materi sedang disiapkan oleh fasilitator.
        </div>

        <div v-else class="materials-list">
          <div v-for="(mat, idx) in materials" :key="mat.id" class="material-card"
               :style="`animation-delay: ${idx * 0.07}s`">
            <div class="mat-header">
              <div class="mat-num">{{ idx + 1 }}</div>
              <h4 class="mat-title">{{ mat.title }}</h4>
            </div>
            <div class="mat-content">{{ mat.content }}</div>
            <div v-if="mat.media_url" class="mat-media">
              <a :href="mat.media_url" target="_blank" class="media-link">
                <span class="media-icon">&#9654;</span>
                Buka Tautan Media / Video &rarr;
              </a>
            </div>
          </div>
        </div>

        <!-- Quiz CTA -->
        <div v-if="hasQuiz" class="quiz-cta">
          <div class="quiz-cta-inner">
            <h3 class="quiz-cta-title">Sudah Selesai Mempelajari Materi?</h3>
            <p class="quiz-cta-desc">Buktikan pemahaman Anda dengan mengikuti Evaluasi Akhir. Nilai yang baik akan membuka akses ke E-Certificate.</p>
            <router-link :to="{ name: 'lms-training-quiz', params: { id: training.id } }" class="quiz-cta-btn">
              Mulai Evaluasi Sekarang &rarr;
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  min-height: 80vh;
}

/* States */
.state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 5rem 2rem;
}
.state-text { color: #6b7280; font-weight: 500; }
.spinner {
  width: 52px; height: 52px;
  border: 4px solid #e5e7eb;
  border-top-color: var(--gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.state-error {
  background: #fef2f2; color: #dc2626;
  border: 1px solid #fecaca; border-radius: 14px;
  padding: 2rem; text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 1rem;
}
.back-link { color: #b91c1c; font-weight: 600; font-size: 0.9rem; text-decoration: underline; }

/* Back button */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--brown);
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  margin-bottom: 1.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  background: white;
  border: 1px solid #f0ebe4;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: all 0.2s;
}
.back-btn:hover { color: var(--maroon); background: #faf6f0; transform: translateX(-2px); }

/* Hero Card */
.hero-card {
  background: white;
  border-radius: 24px;
  border: 1px solid #f0ebe4;
  box-shadow: 0 8px 32px rgba(92, 64, 51, 0.08);
  overflow: hidden;
  position: relative;
  margin-bottom: 2rem;
  animation: fadeDown 0.5s ease-out;
}
.hero-deco {
  position: absolute;
  top: -60px; right: -60px;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(212, 172, 13, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.hero-body {
  padding: 2rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
@media (min-width: 700px) {
  .hero-body { flex-direction: row; align-items: flex-start; justify-content: space-between; gap: 2rem; }
}
.hero-left { flex: 1; }

.status-pill {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}
.pill-published { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.pill-draft { background: #fefce8; color: #ca8a04; border: 1px solid #fde68a; }

.hero-title {
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  font-weight: 800;
  color: #111827;
  line-height: 1.3;
  margin: 0 0 0.75rem 0;
}
.hero-desc {
  color: #4b5563;
  line-height: 1.7;
  font-size: 0.95rem;
}

.enroll-box {
  background: #faf6f0;
  border: 1px solid rgba(212, 172, 13, 0.2);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  text-align: center;
  min-width: 200px;
  flex-shrink: 0;
}
.enroll-label { font-weight: 700; color: var(--brown); font-size: 0.9rem; margin-bottom: 0.75rem; }
.enroll-btn {
  display: block; width: 100%;
  background: linear-gradient(135deg, var(--maroon), var(--brown-dark));
  color: white; font-weight: 700;
  padding: 0.75rem 1.5rem;
  border: none; border-radius: 12px;
  font-size: 0.95rem; cursor: pointer;
  box-shadow: 0 4px 12px rgba(123, 36, 28, 0.25);
  transition: all 0.2s;
}
.enroll-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(123, 36, 28, 0.35); }
.enroll-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.enrolled-badge {
  display: flex; align-items: center; gap: 0.75rem;
  background: white; border-radius: 12px; padding: 1rem;
  border: 1px solid #d1fae5;
}
.check-icon {
  width: 40px; height: 40px;
  background: #16a34a; color: white;
  border-radius: 50%; font-size: 1.25rem;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; flex-shrink: 0;
}
.enrolled-text { font-weight: 700; color: #16a34a; font-size: 0.9rem; }
.enrolled-sub { color: #6b7280; font-size: 0.75rem; }

/* Materials */
.materials-section { animation: fadeUp 0.4s ease-out; }
.section-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.section-bar { width: 6px; height: 28px; background: var(--gold); border-radius: 4px; }
.section-title { font-size: 1.4rem; font-weight: 800; color: #1f2937; margin: 0; }

.empty-materials {
  background: #f9fafb; border: 2px dashed #e5e7eb;
  border-radius: 16px; padding: 3rem; text-align: center; color: #9ca3af;
}

.materials-list { display: flex; flex-direction: column; gap: 1rem; }

.material-card {
  background: white; border: 1px solid #f0ebe4;
  border-radius: 16px; overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  animation: fadeUp 0.4s ease-out both;
  transition: box-shadow 0.2s;
}
.material-card:hover { box-shadow: 0 6px 20px rgba(92, 64, 51, 0.1); }

.mat-header {
  background: #faf6f0;
  padding: 1rem 1.5rem;
  display: flex; align-items: center; gap: 0.875rem;
  border-bottom: 1px solid #f0ebe4;
}
.mat-num {
  width: 36px; height: 36px;
  background: var(--brown); color: white;
  border-radius: 10px; font-weight: 700; font-size: 1rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.mat-title { font-size: 1rem; font-weight: 700; color: var(--brown-dark); margin: 0; }
.mat-content {
  padding: 1.25rem 1.5rem;
  color: #374151; line-height: 1.75;
  font-size: 0.9rem; white-space: pre-wrap;
}
.mat-media {
  background: #faf6f0; padding: 1rem 1.5rem;
  border-top: 1px solid rgba(212, 172, 13, 0.2);
}
.media-link {
  display: inline-flex; align-items: center; gap: 0.5rem;
  color: var(--maroon); font-weight: 600;
  text-decoration: none; font-size: 0.875rem;
  transition: color 0.2s;
}
.media-link:hover { color: var(--brown); }
.media-icon {
  background: white; border-radius: 8px;
  padding: 0.3rem 0.4rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  font-size: 0.75rem;
}

/* Quiz CTA */
.quiz-cta {
  margin-top: 2rem; margin-bottom: 2rem;
  border: 2px solid var(--gold);
  border-radius: 20px; overflow: hidden;
}
.quiz-cta-inner {
  background: linear-gradient(135deg, #faf6f0 0%, #fff 100%);
  padding: 2.5rem 2rem; text-align: center;
}
.quiz-cta-title { font-size: 1.4rem; font-weight: 800; color: #1f2937; margin: 0 0 0.5rem 0; }
.quiz-cta-desc { color: #6b7280; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.6; }
.quiz-cta-btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: var(--brown); color: white;
  font-weight: 700; font-size: 1rem;
  padding: 0.875rem 2rem; border-radius: 14px;
  text-decoration: none;
  box-shadow: 0 6px 16px rgba(92, 64, 51, 0.25);
  transition: all 0.2s;
}
.quiz-cta-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(92, 64, 51, 0.35); }

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .page-container { padding: 1.25rem 1rem; }
}
</style>
