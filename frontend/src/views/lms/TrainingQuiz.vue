<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import lmsService from '../../services/lms'

const route = useRoute()
const router = useRouter()
const trainingId = route.params.id

const quiz = ref(null)
const questions = ref([])
const answers = ref({}) // { question_id: 'answer' }
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const result = ref(null)

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
  if (Object.keys(answers.value).length < questions.value.length) {
    alert('Harap jawab semua pertanyaan sebelum mengumpulkan.')
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
    alert(err.response?.data?.detail || 'Gagal mengirimkan jawaban')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <h2 style="color: var(--brown);">Evaluasi Pelatihan</h2>
    </div>

    <div v-if="loading" class="empty-row">Memuat kuis...</div>
    <div v-else-if="error" class="alert-error">{{ error }}</div>
    <div v-else-if="result" class="stat-card" style="text-align: center; padding: 3rem 1.5rem;">
      <div style="font-size: 4rem; margin-bottom: 1rem;">
        {{ result.passed ? '🎉' : '😔' }}
      </div>
      <h2 style="color: var(--brown); margin-bottom: 1rem;">{{ result.message }}</h2>
      <p style="font-size: 1.2rem; margin-bottom: 2rem;">
        Skor Anda: <strong>{{ result.total_score }}</strong>
      </p>
      
      <router-link to="/admin/enrollments" class="btn-primary">
        Lihat Riwayat Pelatihan Saya
      </router-link>
    </div>
    
    <div v-else-if="quiz">
      <div class="table-card" style="padding: 2rem; margin-bottom: 2rem;">
        <h3 style="margin-bottom: 0.5rem;">{{ quiz.title }}</h3>
        <p style="color: #8a7a6d; font-size: 0.9rem; margin-bottom: 2rem;">
          Waktu Pengerjaan: {{ quiz.time_limit_minutes }} menit
        </p>

        <div v-for="(q, index) in questions" :key="q.id" style="margin-bottom: 2rem; border-bottom: 1px solid #eadfd3; padding-bottom: 1.5rem;">
          <p style="font-weight: 600; margin-bottom: 1rem; font-size: 1.05rem;">
            {{ index + 1 }}. {{ q.question_text }}
          </p>
          <div style="display: flex; flex-direction: column; gap: 0.75rem;">
            <label v-for="(opt, oIndex) in q.parsedOptions" :key="oIndex" style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
              <input type="radio" :name="'question-' + q.id" :value="opt" v-model="answers[q.id]" style="width: 1.2rem; height: 1.2rem; accent-color: var(--brown);">
              <span style="font-size: 0.95rem;">{{ opt }}</span>
            </label>
          </div>
        </div>

        <div style="text-align: right; margin-top: 2rem;">
          <button class="btn-primary" @click="submit" :disabled="submitting">
            {{ submitting ? 'Mengirim...' : 'Kumpulkan Jawaban' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
