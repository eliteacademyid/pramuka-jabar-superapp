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
  <div class="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 min-h-[80vh] flex flex-col">
    <!-- State: Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center space-y-4 animate-pulse mt-12">
      <div class="w-16 h-16 border-4 border-[var(--gold)] border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-500 font-medium">Memuat evaluasi...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200 text-center shadow-sm animate-fade-in mt-12">
      <span class="text-2xl block mb-2">⚠️</span>
      {{ error }}
      <div class="mt-4">
        <router-link to="/admin/enrollments" class="text-red-700 underline font-medium">Kembali ke Pelatihanku</router-link>
      </div>
    </div>

    <!-- Result View -->
    <div v-else-if="result" class="animate-fade-in-down mt-12">
      <div class="bg-white rounded-3xl p-8 sm:p-12 shadow-2xl border-2 border-[var(--gold)]/20 text-center relative overflow-hidden">
        <!-- Confetti bg if passed -->
        <div v-if="result.passed" class="absolute inset-0 bg-gradient-to-br from-green-50 to-green-100 opacity-50"></div>
        <div v-else class="absolute inset-0 bg-gradient-to-br from-red-50 to-red-100 opacity-50"></div>
        
        <div class="relative z-10">
          <div class="text-7xl mb-6 animate-bounce">
            {{ result.passed ? '🎉' : '😔' }}
          </div>
          <h2 class="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-2">
            {{ result.message }}
          </h2>
          <p class="text-gray-600 mb-8 text-lg">
            Skor Akhir Anda: <span class="text-3xl font-black" :class="result.passed ? 'text-green-600' : 'text-red-600'">{{ result.total_score }}</span>
          </p>
          
          <router-link to="/admin/enrollments" 
             class="inline-block bg-gradient-to-r from-[var(--brown)] to-[var(--brown-dark)] text-white font-bold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all">
            Lihat Riwayat Pelatihan Saya
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- Quiz View -->
    <div v-else-if="quiz" class="animate-fade-in">
      <div class="flex items-center gap-4 mb-8">
        <router-link :to="{ name: 'lms-training-detail', params: { id: trainingId } }" class="text-[var(--brown)] hover:text-[var(--maroon)] font-bold bg-white p-2 rounded-lg shadow-sm">&larr; Batal</router-link>
        <div>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-gray-900">{{ quiz.title }}</h2>
          <p class="text-sm text-gray-500 font-medium mt-1">⏳ Waktu Pengerjaan: {{ quiz.time_limit_minutes }} menit</p>
        </div>
      </div>

      <div class="bg-white rounded-3xl shadow-lg border border-gray-100 p-6 sm:p-10">
        <div class="space-y-10">
          <div v-for="(q, index) in questions" :key="q.id" 
               class="p-6 bg-gray-50 border border-gray-100 rounded-2xl relative transition-all duration-300 hover:shadow-md hover:border-[var(--gold)]/30"
               :style="`animation: fade-in-up 0.5s ease forwards; animation-delay: ${index * 0.1}s; opacity: 0;`">
            
            <div class="absolute -top-3 -left-3 w-8 h-8 bg-[var(--brown)] text-white font-bold rounded-lg flex items-center justify-center shadow-md">
              {{ index + 1 }}
            </div>
            
            <p class="font-semibold text-gray-800 text-lg mb-6 pl-4">
              {{ q.question_text }}
            </p>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 pl-4">
              <label v-for="(opt, oIndex) in q.parsedOptions" :key="oIndex" 
                class="flex items-center p-4 bg-white border-2 rounded-xl cursor-pointer transition-all duration-200"
                :class="answers[q.id] === opt ? 'border-[var(--brown)] shadow-[0_0_0_1px_var(--brown)] bg-[#faf6f0]' : 'border-gray-200 hover:border-[var(--gold)]'">
                <div class="relative flex items-center justify-center w-5 h-5 mr-3 border-2 rounded-full"
                     :class="answers[q.id] === opt ? 'border-[var(--brown)]' : 'border-gray-300'">
                  <div class="w-2.5 h-2.5 rounded-full bg-[var(--brown)] transition-transform duration-200"
                       :class="answers[q.id] === opt ? 'scale-100' : 'scale-0'"></div>
                </div>
                <input type="radio" :name="'question-' + q.id" :value="opt" v-model="answers[q.id]" class="sr-only">
                <span class="text-gray-700 font-medium">{{ opt }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="mt-12 flex justify-end">
          <button @click="submit" :disabled="submitting" 
            class="bg-gradient-to-r from-[var(--maroon)] to-[var(--brown)] text-white font-bold py-4 px-10 rounded-2xl shadow-[0_10px_20px_rgba(123,36,28,0.2)] hover:shadow-[0_15px_30px_rgba(123,36,28,0.3)] hover:-translate-y-1 active:scale-95 transition-all disabled:opacity-70 disabled:hover:translate-y-0 disabled:active:scale-100 flex items-center gap-2">
            <span v-if="submitting" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            {{ submitting ? 'Memproses Jawaban...' : 'Kumpulkan Jawaban ✨' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in-down {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fade-in-up {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-down {
  animation: fade-in-down 0.6s ease-out forwards;
}
.animate-fade-in {
  animation: fade-in-up 0.4s ease-out forwards;
}
</style>
