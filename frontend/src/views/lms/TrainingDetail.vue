<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import lmsService from '../../services/lms'

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

onMounted(async () => {
  await fetchTrainingData()
})

async function fetchTrainingData() {
  loading.value = true
  error.value = ''
  try {
    // 1. Get training detail (we reuse the list for now since there's no single detail endpoint)
    // OR we just find it from the list
    const tRes = await lmsService.getTrainings()
    training.value = tRes.data.find(t => t.id == trainingId)

    if (!training.value) {
      error.value = 'Pelatihan tidak ditemukan'
      return
    }

    // 2. Check if enrolled
    const eRes = await lmsService.getMyEnrollments()
    const enrollment = eRes.data.find(e => e.training_id == trainingId)
    isEnrolled.value = !!enrollment

    if (isEnrolled.value) {
      // 3. Get materials
      const mRes = await lmsService.getTrainingMaterials(trainingId)
      materials.value = mRes.data
      
      // 4. Check if quiz exists
      try {
        await lmsService.getQuiz(trainingId)
        hasQuiz.value = true
      } catch (qErr) {
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
    await fetchTrainingData() // Refresh to get materials
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mendaftar pelatihan')
  } finally {
    enrolling.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8 min-h-[80vh] flex flex-col">
    <!-- State: Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center space-y-4 animate-pulse mt-12">
      <div class="w-16 h-16 border-4 border-[var(--gold)] border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-500 font-medium">Memuat detail pelatihan...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200 text-center shadow-sm animate-fade-in mt-12">
      <span class="text-2xl block mb-2">Pemberitahuan</span>
      {{ error }}
      <div class="mt-4">
        <router-link to="/admin/trainings" class="text-red-700 underline font-medium">Kembali ke Daftar</router-link>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="training" class="animate-fade-in-down">
      
      <!-- Breadcrumb / Back -->
      <router-link to="/admin/trainings" class="inline-flex items-center gap-2 text-[var(--brown)] hover:text-[var(--maroon)] font-semibold transition-colors mb-6 group">
        <span class="group-hover:-translate-x-1 transition-transform">&larr;</span> Kembali ke Daftar
      </router-link>

      <!-- Header Card -->
      <div class="bg-white rounded-3xl p-6 sm:p-10 shadow-lg border border-gray-100 relative overflow-hidden mb-8">
        <!-- Decorative blobs -->
        <div class="absolute -top-10 -right-10 w-48 h-48 bg-gradient-to-br from-[var(--gold)] to-[var(--brown)] opacity-10 rounded-full blur-3xl"></div>
        <div class="absolute -bottom-10 -left-10 w-48 h-48 bg-gradient-to-tr from-[var(--maroon)] to-[var(--brown)] opacity-10 rounded-full blur-3xl"></div>

        <div class="relative z-10 flex flex-col md:flex-row gap-6 justify-between items-start md:items-center">
          <div>
            <span :class="[
              'inline-block px-3 py-1 text-xs font-bold rounded-full mb-3',
              training.status === 'Published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
            ]">
              {{ training.status === 'Published' ? 'Tersedia' : 'Draft' }}
            </span>
            <h2 class="text-3xl md:text-4xl font-extrabold text-gray-900 leading-tight mb-4">
              {{ training.title }}
            </h2>
            <p class="text-gray-600 text-lg leading-relaxed max-w-2xl">
              {{ training.description }}
            </p>
          </div>
          
          <div class="bg-[#faf6f0] p-6 rounded-2xl w-full md:w-auto text-center shrink-0 border border-[var(--gold)]/30">
            <div v-if="!isEnrolled">
              <h3 class="font-bold text-[var(--brown)] mb-3">Siap Belajar?</h3>
              <button @click="enroll" :disabled="enrolling" 
                class="w-full bg-gradient-to-r from-[var(--maroon)] to-[var(--brown-dark)] text-white font-bold py-3 px-8 rounded-xl shadow-md hover:shadow-lg active:scale-95 transition-all disabled:opacity-70 disabled:active:scale-100">
                {{ enrolling ? 'Memproses...' : 'Daftar Sekarang' }}
              </button>
            </div>
            <div v-else class="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-3">
              <div class="text-3xl grayscale opacity-50 block text-[var(--gold)]">Terdaftar</div>
              <div>
                <p class="font-bold text-green-600">Terdaftar</p>
                <p class="text-xs text-gray-500">Anda sudah memiliki akses</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modules Area (If Enrolled) -->
      <div v-if="isEnrolled" class="animate-fade-in">
        <div class="flex items-center gap-4 mb-8">
          <div class="h-10 w-2 bg-[var(--gold)] rounded-full"></div>
          <h3 class="text-2xl font-bold text-gray-800">Modul Pembelajaran</h3>
        </div>
        
        <div v-if="materials.length === 0" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-10 text-center text-gray-500">
          Modul materi sedang disiapkan oleh fasilitator.
        </div>
        
        <div v-else class="space-y-6">
          <div v-for="(mat, idx) in materials" :key="mat.id" 
               class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden group hover:shadow-md transition-shadow animate-fade-in"
               :style="`animation-delay: ${idx * 0.1}s;`">
            
            <div class="border-b border-gray-50 bg-gray-50/50 p-4 sm:p-6 flex items-center gap-4">
              <div class="w-10 h-10 shrink-0 bg-[var(--brown)] text-white font-bold rounded-xl flex items-center justify-center text-lg shadow-inner">
                {{ idx + 1 }}
              </div>
              <h4 class="text-xl font-bold text-[var(--brown-dark)]">
                {{ mat.title }}
              </h4>
            </div>
            
            <div class="p-4 sm:p-6 text-gray-700 leading-relaxed whitespace-pre-wrap text-sm sm:text-base">
              {{ mat.content }}
            </div>
            
            <div v-if="mat.media_url" class="bg-[#faf6f0] p-4 sm:p-6 border-t border-[var(--gold)]/20">
              <a :href="mat.media_url" target="_blank" 
                 class="inline-flex items-center gap-2 text-[var(--maroon)] font-bold hover:text-[var(--brown)] transition-colors group/link">
                <span class="p-2 bg-white rounded-lg shadow-sm group-hover/link:shadow group-hover/link:-translate-y-0.5 transition-all block w-8 h-8 flex items-center justify-center">▶</span>
                Buka Tautan Media / Video
                <span class="group-hover/link:translate-x-1 transition-transform">&rarr;</span>
              </a>
            </div>
          </div>
        </div>
        
        <!-- Quiz Section -->
        <div v-if="hasQuiz" class="mt-12 mb-8 relative">
          <div class="absolute inset-0 bg-gradient-to-r from-[var(--brown)] to-[var(--maroon)] rounded-3xl transform -rotate-1 opacity-20"></div>
          <div class="relative bg-white rounded-3xl p-8 sm:p-12 text-center border-2 border-[var(--gold)] shadow-xl flex flex-col items-center">
            <span class="text-5xl mb-4 opacity-50 block grayscale">Evaluasi</span>
            <h3 class="text-2xl font-extrabold text-gray-900 mb-2">Sudah Selesai Mempelajari Materi?</h3>
            <p class="text-gray-500 mb-8 max-w-md">Buktikan pemahaman Anda dengan mengikuti Evaluasi Akhir. Nilai yang baik akan membuka akses ke E-Certificate.</p>
            
            <router-link :to="{ name: 'lms-training-quiz', params: { id: training.id } }" 
               class="inline-flex items-center justify-center gap-3 bg-[var(--brown)] text-white font-bold text-lg py-4 px-10 rounded-2xl shadow-[0_10px_20px_rgba(92,64,51,0.3)] hover:shadow-[0_15px_30px_rgba(92,64,51,0.4)] hover:-translate-y-1 active:translate-y-0 transition-all">
              Mulai Evaluasi Sekarang
            </router-link>
          </div>
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
