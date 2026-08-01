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
  <div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 min-h-[80vh] flex flex-col">
    
    <!-- Header -->
    <div class="mb-10 animate-fade-in-down">
      <h2 class="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-[var(--brown)] to-[var(--gold)] mb-2">
        Katalog e-Pelatihan
      </h2>
      <p class="text-gray-500 text-sm sm:text-base">Tingkatkan kompetensi Pramuka Anda melalui modul pembelajaran mandiri yang interaktif.</p>
    </div>

    <!-- State: Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center space-y-4 animate-pulse">
      <div class="w-16 h-16 border-4 border-[var(--gold)] border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-500 font-medium">Memuat katalog pelatihan...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200 text-center shadow-sm animate-fade-in">
      <span class="text-2xl block mb-2">⚠️</span>
      {{ error }}
    </div>

    <!-- State: Empty -->
    <div v-else-if="trainings.length === 0" class="flex-1 flex flex-col items-center justify-center text-center p-12 bg-white/50 backdrop-blur-sm rounded-3xl border border-dashed border-gray-300 animate-fade-in">
      <span class="text-6xl mb-4 grayscale opacity-50">⛺</span>
      <h3 class="text-xl font-bold text-gray-700 mb-2">Belum ada pelatihan tersedia</h3>
      <p class="text-gray-500">Silakan kembali lagi nanti saat admin sudah mempublikasikan modul baru.</p>
    </div>
    
    <!-- Content: Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
      <div v-for="(training, index) in trainings" :key="training.id" 
           class="group bg-white rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-100 hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 flex flex-col relative overflow-hidden"
           :style="`animation: fade-in-up 0.5s ease forwards; animation-delay: ${index * 0.1}s; opacity: 0;`">
        
        <!-- Decorative bg -->
        <div class="absolute -top-16 -right-16 w-32 h-32 bg-gradient-to-br from-[var(--gold)] to-[var(--brown)] opacity-10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-500"></div>

        <div class="mb-4">
          <span class="inline-block px-3 py-1 bg-[#faf6f0] text-[var(--brown)] text-xs font-bold rounded-full mb-3 tracking-wide">LMS PROGRAM</span>
          <h3 class="text-xl font-bold text-gray-900 group-hover:text-[var(--maroon)] transition-colors leading-tight">
            {{ training.title }}
          </h3>
        </div>
        
        <p class="text-sm text-gray-500 mb-6 flex-1 line-clamp-3">
          {{ training.description || 'Pelatihan ini tidak memiliki deskripsi khusus. Silakan masuk untuk melihat detail modul.' }}
        </p>
        
        <div class="bg-gray-50 rounded-2xl p-4 mb-6 space-y-2 text-xs sm:text-sm text-gray-600 border border-gray-100">
          <div class="flex justify-between items-center">
            <span class="flex items-center gap-1.5 font-medium"><span class="text-[var(--gold)]">📅</span> Mulai</span>
            <span class="font-semibold text-gray-800">{{ formatDate(training.start_date) }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="flex items-center gap-1.5 font-medium"><span class="text-[var(--brown)]">🎯</span> KKM</span>
            <span class="font-semibold text-gray-800">{{ training.passing_grade }} Poin</span>
          </div>
        </div>
        
        <router-link :to="{ name: 'lms-training-detail', params: { id: training.id } }" 
           class="w-full text-center py-3 px-4 bg-gradient-to-r from-[var(--brown)] to-[var(--brown-dark)] text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-[var(--brown)]/30 active:scale-95 transition-all relative overflow-hidden">
          <span class="relative z-10">Lihat Detail Modul &rarr;</span>
          <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
        </router-link>
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
