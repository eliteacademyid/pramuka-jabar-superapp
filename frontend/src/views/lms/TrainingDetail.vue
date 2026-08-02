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
const openMaterial = ref(null) // idx of currently opened material
const modal = ref({ show: false, type: 'success', title: '', message: '' })

function toggleMaterial(idx) {
  openMaterial.value = openMaterial.value === idx ? null : idx
}

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

// ── Media helpers ──────────────────────────────────────────
function getMediaType(url) {
  if (!url) return null
  try {
    const u = new URL(url)
    if (u.hostname.includes('youtube.com') || u.hostname.includes('youtu.be')) return 'youtube'
    if (u.hostname.includes('drive.google.com')) return 'gdrive'
    if (/\.(mp4|webm|ogg)$/i.test(u.pathname)) return 'video'
    if (/\.(pdf)$/i.test(u.pathname)) return 'pdf'
    return 'link'
  } catch { return 'link' }
}

function getEmbedUrl(url) {
  if (!url) return ''
  try {
    const u = new URL(url)
    // YouTube watch?v=ID or youtu.be/ID or embed
    if (u.hostname.includes('youtu.be')) {
      return `https://www.youtube.com/embed${u.pathname}?rel=0`
    }
    if (u.hostname.includes('youtube.com')) {
      const v = u.searchParams.get('v') || u.pathname.replace('/embed/', '')
      if (v) return `https://www.youtube.com/embed/${v}?rel=0`
    }
    // Google Drive share link → embed
    if (u.hostname.includes('drive.google.com')) {
      const m = u.pathname.match(/\/d\/([^/]+)/)
      if (m) return `https://drive.google.com/file/d/${m[1]}/preview`
    }
    return url
  } catch { return url }
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
               :class="openMaterial === idx ? 'mat-open' : ''"
               :style="`animation-delay: ${idx * 0.07}s`">
            <!-- Accordion Header (always visible, clickable) -->
            <div class="mat-header" @click="toggleMaterial(idx)" style="cursor:pointer">
              <div class="mat-num">{{ idx + 1 }}</div>
              <h4 class="mat-title">{{ mat.title }}</h4>
              <div class="mat-tags">
                <span v-if="mat.media_url" class="mat-tag-media">
                  {{ getMediaType(mat.media_url) === 'youtube' ? 'Video' :
                     getMediaType(mat.media_url) === 'gdrive' ? 'Drive' :
                     getMediaType(mat.media_url) === 'pdf' ? 'PDF' : 'Media' }}
                </span>
              </div>
              <svg class="mat-chevron" :class="openMaterial === idx ? 'chevron-up' : ''"
                   viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </div>

            <!-- Accordion Body (only shown when open) -->
            <Transition name="accordion">
              <div v-if="openMaterial === idx" class="mat-body">
                <div v-if="mat.content" class="mat-content">{{ mat.content }}</div>

                <!-- Smart Media Embed -->
                <div v-if="mat.media_url" class="mat-media">
                  <!-- YouTube / Google Drive → iframe embed -->
                  <div v-if="getMediaType(mat.media_url) === 'youtube' || getMediaType(mat.media_url) === 'gdrive'"
                       class="media-embed-wrap">
                    <div class="media-label">
                      <svg viewBox="0 0 24 24" fill="currentColor" class="media-label-icon">
                        <path v-if="getMediaType(mat.media_url) === 'youtube'"
                              d="M23.5 6.2a3 3 0 00-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 00.5 6.2 31 31 0 000 12a31 31 0 00.5 5.8 3 3 0 002.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 002.1-2.1A31 31 0 0024 12a31 31 0 00-.5-5.8zM9.75 15.5V8.5l6.5 3.5-6.5 3.5z"/>
                        <path v-else d="M19 2H5C3.34 2 2 3.34 2 5v14c0 1.66 1.34 3 3 3h14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3zM9 17H7v-7h2v7zm-1-8c-.66 0-1.2-.54-1.2-1.2S7.34 6.6 8 6.6s1.2.54 1.2 1.2S8.66 9 8 9zm9 8h-2v-4c0-.55-.45-1-1-1s-1 .45-1 1v4h-2v-7h2v1.07c.52-.8 1.56-1.3 2.5-1.07C17.34 11.28 17 12 17 13v4z"/>
                      </svg>
                      {{ getMediaType(mat.media_url) === 'youtube' ? 'YouTube Video' : 'Google Drive' }}
                    </div>
                    <iframe
                      :src="getEmbedUrl(mat.media_url)"
                      class="media-iframe"
                      allowfullscreen
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      loading="lazy"
                      frameborder="0">
                    </iframe>
                  </div>

                  <!-- Native video file -->
                  <div v-else-if="getMediaType(mat.media_url) === 'video'" class="media-embed-wrap">
                    <div class="media-label">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="media-label-icon">
                        <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>
                      </svg>
                      Video
                    </div>
                    <video :src="mat.media_url" controls class="media-video">Browser tidak mendukung video.</video>
                  </div>

                  <!-- PDF embed -->
                  <div v-else-if="getMediaType(mat.media_url) === 'pdf'" class="media-embed-wrap">
                    <div class="media-label">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="media-label-icon">
                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
                      </svg>
                      Dokumen PDF
                    </div>
                    <iframe :src="mat.media_url" class="media-iframe media-pdf" frameborder="0"></iframe>
                  </div>

                  <!-- Fallback link -->
                  <div v-else class="media-link-row">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="link-icon">
                      <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                      <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                    </svg>
                    <a :href="mat.media_url" target="_blank" rel="noopener noreferrer" class="media-ext-link">
                      Buka Tautan Materi Eksternal &rarr;
                    </a>
                  </div>
                </div>

                <div v-if="!mat.content && !mat.media_url" class="mat-empty">
                  Konten materi belum tersedia.
                </div>
              </div>
            </Transition>
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
  border-bottom: 1px solid #f5f0eb;
}
.mat-body { overflow: hidden; }
.mat-empty {
  padding: 1.25rem 1.5rem;
  color: #9ca3af; font-style: italic; font-size: 0.85rem;
}

/* Accordion header extras */
.mat-header {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 1rem 1.5rem;
  background: #faf6f0;
  border-bottom: 1px solid #f0ebe4;
  user-select: none;
  transition: background 0.15s;
}
.mat-header:hover { background: #f5ede0; }
.mat-open > .mat-header {
  background: linear-gradient(90deg, #faf0db, #faf6f0);
  border-left: 3px solid var(--gold);
  padding-left: calc(1.5rem - 3px);
}
.mat-tags { display: flex; gap: 0.35rem; margin-left: auto; }
.mat-tag-media {
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em;
  padding: 0.15rem 0.5rem; border-radius: 999px;
  background: #ffe4b5; color: #92400e;
}
.mat-chevron {
  width: 18px; height: 18px; flex-shrink: 0;
  color: #9ca3af; transition: transform 0.25s ease;
}
.chevron-up { transform: rotate(180deg); }

/* Accordion transition */
.accordion-enter-active { animation: slideDown 0.25s ease-out; }
.accordion-leave-active { animation: slideDown 0.2s ease-in reverse; }
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.mat-media {
  background: #fafafa; 
  border-top: 1px solid #f0ebe4;
  padding: 0;
}

/* Media embed wrapper */
.media-embed-wrap { display: flex; flex-direction: column; }
.media-label {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #faf6f0; border-bottom: 1px solid #f0ebe4;
  font-size: 0.78rem; font-weight: 700;
  color: var(--brown); letter-spacing: 0.03em;
}
.media-label-icon { width: 16px; height: 16px; flex-shrink: 0; }

/* Responsive iframe (16:9) */
.media-iframe {
  width: 100%;
  aspect-ratio: 16 / 9;
  border: none;
  background: #000;
  display: block;
}
.media-pdf { aspect-ratio: auto; height: 480px; }

/* Native video */
.media-video {
  width: 100%; max-height: 480px;
  background: #000; display: block;
}

/* External link row */
.media-link-row {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 1rem 1.25rem;
}
.link-icon { width: 18px; height: 18px; color: var(--maroon); flex-shrink: 0; }
.media-ext-link {
  color: var(--maroon); font-weight: 600; font-size: 0.875rem;
  text-decoration: none; transition: color 0.2s;
}
.media-ext-link:hover { color: var(--brown); text-decoration: underline; }


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
