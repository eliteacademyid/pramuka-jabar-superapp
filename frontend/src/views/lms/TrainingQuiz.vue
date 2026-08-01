<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import lmsService from '../../services/lms'
import ActionModal from '../../components/ActionModal.vue'

const route = useRoute()
const router = useRouter()
const trainingId = route.params.id

const quiz = ref(null)
const questions = ref([])
const answers = ref({})
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const result = ref(null)
const modal = ref({ show: false, type: 'success', title: '', message: '' })

function showModal(type, title, message) {
  modal.value = { show: true, type, title, message }
}

const answeredCount = computed(() => Object.keys(answers.value).length)

onMounted(async () => {
  try {
    const qRes = await lmsService.getQuiz(trainingId)
    quiz.value = qRes.data

    if (quiz.value) {
      const qnRes = await lmsService.getQuizQuestions(quiz.value.id)
      questions.value = qnRes.data.map(q => ({
        ...q,
        parsedOptions: JSON.parse(q.options)
      }))
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Gagal memuat kuis'
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (answeredCount.value < questions.value.length) {
    showModal('warning', 'Belum Lengkap', `Masih ada ${questions.value.length - answeredCount.value} pertanyaan yang belum dijawab. Harap jawab semua pertanyaan terlebih dahulu.`)
    return
  }

  const payload = {
    answers: Object.keys(answers.value).map(qId => ({
      question_id: parseInt(qId),
      answer: answers.value[qId]
    }))
  }

  submitting.value = true
  try {
    const res = await lmsService.submitQuiz(quiz.value.id, payload)
    result.value = res.data
  } catch (err) {
    showModal('error', 'Gagal Mengirim', err.response?.data?.detail || 'Gagal mengirimkan jawaban. Silakan coba lagi.')
  } finally {
    submitting.value = false
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
      <p class="state-text">Memuat evaluasi...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="state-error">
      {{ error }}
      <router-link to="/admin/enrollments" class="back-link">Kembali ke Pelatihanku</router-link>
    </div>

    <!-- Result Overlay -->
    <div v-if="result" class="result-overlay">
      <div :class="['result-card', result.passed ? 'result-pass' : 'result-fail']">
        <div class="result-bg"></div>
        <div class="result-body">
          <div :class="['result-verdict', result.passed ? 'verdict-pass' : 'verdict-fail']">
            {{ result.passed ? 'LULUS' : 'TIDAK LULUS' }}
          </div>
          <h2 class="result-message">{{ result.message }}</h2>
          <p class="result-score-label">Skor Akhir Anda</p>
          <div :class="['result-score', result.passed ? 'score-pass' : 'score-fail']">
            {{ result.total_score }}
          </div>
          <router-link to="/admin/enrollments" class="result-btn">
            Lihat Riwayat Pelatihan
          </router-link>
        </div>
      </div>
    </div>

    <!-- Quiz View -->
    <div v-else-if="quiz" class="quiz-wrap">

      <!-- Top bar -->
      <div class="quiz-topbar">
        <router-link :to="{ name: 'lms-training-detail', params: { id: trainingId } }" class="back-btn">
          &larr; Batal
        </router-link>
        <div class="quiz-meta">
          <h2 class="quiz-title">{{ quiz.title }}</h2>
          <p class="quiz-time">Waktu: {{ quiz.time_limit_minutes }} menit</p>
        </div>
        <div class="quiz-progress">
          <span class="progress-count">{{ answeredCount }}/{{ questions.length }}</span>
          <span class="progress-label">Dijawab</span>
        </div>
      </div>

      <!-- Questions -->
      <div class="questions-list">
        <div v-for="(q, index) in questions" :key="q.id"
             class="question-card"
             :class="answers[q.id] ? 'q-answered' : ''"
             :style="`animation-delay: ${index * 0.06}s`">

          <div class="q-number">{{ index + 1 }}</div>
          <div class="q-body">
            <p class="q-text">{{ q.question_text }}</p>
            <div class="options-grid">
              <label v-for="(opt, oIndex) in q.parsedOptions" :key="oIndex"
                     :class="['option-label', answers[q.id] === opt ? 'option-selected' : '']">
                <input type="radio" :name="'q-' + q.id" :value="opt" v-model="answers[q.id]" class="radio-hidden">
                <span :class="['radio-dot', answers[q.id] === opt ? 'dot-filled' : '']"></span>
                <span class="option-text">{{ opt }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- Submit -->
      <div class="submit-row">
        <div class="submit-info">
          <span :class="answeredCount === questions.length ? 'info-done' : 'info-pending'">
            {{ answeredCount === questions.length ? 'Semua pertanyaan telah dijawab' : `${questions.length - answeredCount} pertanyaan belum dijawab` }}
          </span>
        </div>
        <button @click="submit" :disabled="submitting" class="submit-btn">
          <span v-if="submitting" class="btn-spinner"></span>
          {{ submitting ? 'Memproses...' : 'Kumpulkan Jawaban' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  min-height: 80vh;
}

/* States */
.state-center {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 1rem; padding: 5rem 2rem;
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
.back-link { color: #b91c1c; font-weight: 600; text-decoration: underline; }

/* Result Overlay */
.result-overlay {
  position: fixed; inset: 0; z-index: 200;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(6px);
  padding: 1.5rem;
  animation: fadeIn 0.3s ease;
}
.result-card {
  background: white;
  border-radius: 28px;
  width: 100%; max-width: 440px;
  overflow: hidden;
  box-shadow: 0 25px 60px rgba(0,0,0,0.3);
  position: relative;
  animation: scaleIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.result-pass { border: 2px solid #86efac; }
.result-fail { border: 2px solid #fca5a5; }
.result-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(240,253,244,0.8), rgba(255,255,255,0.9));
  pointer-events: none;
}
.result-fail .result-bg {
  background: linear-gradient(135deg, rgba(254,242,242,0.8), rgba(255,255,255,0.9));
}
.result-body {
  position: relative; z-index: 1;
  padding: 2.5rem 2rem; text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
}
.result-verdict {
  font-size: 2.2rem; font-weight: 900;
  letter-spacing: 0.05em;
  padding: 0.5rem 1.75rem;
  border-radius: 14px;
  margin-bottom: 0.5rem;
}
.verdict-pass { background: #dcfce7; color: #15803d; }
.verdict-fail { background: #fee2e2; color: #b91c1c; }
.result-message { font-size: 1.2rem; font-weight: 700; color: #1f2937; margin: 0; }
.result-score-label { color: #9ca3af; font-size: 0.85rem; margin-top: 0.5rem; }
.result-score { font-size: 3.5rem; font-weight: 900; line-height: 1; }
.score-pass { color: #16a34a; }
.score-fail { color: #dc2626; }
.result-btn {
  display: inline-block; margin-top: 1rem;
  background: linear-gradient(135deg, var(--brown), var(--brown-dark));
  color: white; font-weight: 700;
  padding: 0.8rem 2rem; border-radius: 12px;
  text-decoration: none; font-size: 0.95rem;
  box-shadow: 0 4px 14px rgba(92,64,51,0.25);
  transition: all 0.2s;
}
.result-btn:hover { transform: translateY(-2px); }

/* Quiz Wrap */
.quiz-wrap { animation: fadeUp 0.4s ease-out; }

/* Top Bar */
.quiz-topbar {
  display: flex; align-items: center; gap: 1rem;
  background: white; border-radius: 16px;
  padding: 1.25rem 1.5rem;
  border: 1px solid #f0ebe4;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.back-btn {
  color: var(--brown); font-weight: 600; font-size: 0.875rem;
  text-decoration: none; background: #faf6f0;
  padding: 0.5rem 0.875rem; border-radius: 8px;
  border: 1px solid #f0ebe4; white-space: nowrap;
  transition: all 0.2s; flex-shrink: 0;
}
.back-btn:hover { color: var(--maroon); background: #f5eee6; }
.quiz-meta { flex: 1; }
.quiz-title { font-size: 1.15rem; font-weight: 800; color: #1f2937; margin: 0; }
.quiz-time { font-size: 0.8rem; color: #6b7280; margin: 0.15rem 0 0; }
.quiz-progress {
  display: flex; flex-direction: column; align-items: center;
  background: var(--brown); color: white;
  padding: 0.5rem 1rem; border-radius: 12px;
  text-align: center; flex-shrink: 0;
}
.progress-count { font-size: 1.1rem; font-weight: 800; line-height: 1; }
.progress-label { font-size: 0.65rem; opacity: 0.8; margin-top: 0.1rem; }

/* Questions */
.questions-list { display: flex; flex-direction: column; gap: 1rem; }

.question-card {
  background: white; border: 2px solid #f0ebe4;
  border-radius: 18px; overflow: hidden;
  display: flex; align-items: flex-start; gap: 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  animation: fadeUp 0.4s ease-out both;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.question-card.q-answered {
  border-color: rgba(212, 172, 13, 0.4);
  box-shadow: 0 4px 16px rgba(212, 172, 13, 0.1);
}

.q-number {
  width: 48px; min-height: 48px;
  background: var(--brown); color: white;
  font-weight: 800; font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  align-self: stretch;
}
.question-card.q-answered .q-number { background: var(--gold); }

.q-body { padding: 1.25rem 1.5rem; flex: 1; }
.q-text { font-weight: 600; color: #1f2937; font-size: 0.95rem; margin: 0 0 1rem; line-height: 1.6; }

.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
}
@media (max-width: 520px) { .options-grid { grid-template-columns: 1fr; } }

.option-label {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.7rem 0.875rem;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.option-label:hover { border-color: var(--gold); background: #faf6f0; }
.option-selected {
  border-color: var(--brown) !important;
  background: #faf6f0 !important;
  box-shadow: 0 0 0 1px var(--brown);
}
.radio-hidden { position: absolute; opacity: 0; pointer-events: none; }
.radio-dot {
  width: 18px; height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.dot-filled {
  border-color: var(--brown);
  background: var(--brown);
  box-shadow: inset 0 0 0 3px white;
}
.option-text { font-size: 0.875rem; font-weight: 500; color: #374151; }

/* Submit Row */
.submit-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 1.5rem; gap: 1rem; flex-wrap: wrap;
}
.submit-info { font-size: 0.85rem; font-weight: 500; }
.info-done { color: #16a34a; }
.info-pending { color: #6b7280; }

.submit-btn {
  display: flex; align-items: center; gap: 0.5rem;
  background: linear-gradient(135deg, var(--maroon), var(--brown));
  color: white; font-weight: 700; font-size: 1rem;
  padding: 0.875rem 2rem; border-radius: 14px; border: none;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(123, 36, 28, 0.2);
  transition: all 0.2s;
}
.submit-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(123, 36, 28, 0.3); }
.submit-btn:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }
.btn-spinner {
  width: 18px; height: 18px;
  border: 2px solid white; border-top-color: transparent;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .page-container { padding: 1rem; }
  .quiz-topbar { flex-direction: column; align-items: flex-start; }
  .submit-row { flex-direction: column; align-items: stretch; }
  .submit-btn { justify-content: center; }
}
</style>
