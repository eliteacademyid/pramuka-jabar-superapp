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
      const tRes = await lmsService.getTrainings()
      tRes.data.forEach(t => {
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

const getCertificate = async (enrollmentId) => {
  try {
    const res = await lmsService.getCertificate(enrollmentId)
    const cert = res.data
    alert(`E-Certificate Diterbitkan!\n\nNo: ${cert.certificate_id}\nNama: ${cert.issued_to}\nPelatihan: ${cert.training_title}\nTanggal: ${cert.issue_date}\n\n${cert.message}`)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal mengambil sertifikat')
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 min-h-[80vh] flex flex-col">
    <!-- Header -->
    <div class="mb-10 animate-fade-in-down">
      <h2 class="text-3xl sm:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-[var(--brown)] to-[var(--gold)] mb-2">
        Riwayat Pelatihanku
      </h2>
      <p class="text-gray-500 text-sm sm:text-base">Pantau progres belajar dan unduh sertifikat kelulusan Anda di sini.</p>
    </div>

    <!-- State: Loading -->
    <div v-if="loading" class="flex-1 flex flex-col items-center justify-center space-y-4 animate-pulse">
      <div class="w-16 h-16 border-4 border-[var(--gold)] border-t-transparent rounded-full animate-spin"></div>
      <p class="text-gray-500 font-medium">Memuat data riwayat...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200 text-center shadow-sm animate-fade-in">
      <span class="text-2xl block mb-2">Pemberitahuan</span>
      {{ error }}
    </div>

    <!-- State: Empty -->
    <div v-else-if="enrollments.length === 0" class="flex-1 flex flex-col items-center justify-center text-center p-12 bg-white/50 backdrop-blur-sm rounded-3xl border border-dashed border-gray-300 animate-fade-in">
      <span class="text-6xl mb-4 grayscale opacity-40 block">Kosong</span>
      <h3 class="text-xl font-bold text-gray-700 mb-2">Anda belum mengikuti pelatihan</h3>
      <p class="text-gray-500 mb-6">Jelajahi katalog pelatihan dan mulai tingkatkan kemampuan Anda.</p>
      <router-link to="/admin/trainings" class="btn-primary rounded-xl px-6 py-3 shadow-lg hover:shadow-xl transition-shadow">
        Lihat Katalog Pelatihan
      </router-link>
    </div>

    <!-- Content: Grid of Progress Cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="(e, index) in enrollments" :key="e.id" 
           class="bg-white rounded-3xl p-6 shadow-md border border-gray-100 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 flex flex-col relative animate-fade-in"
           :style="`animation-delay: ${index * 0.1}s;`">
        
        <div class="flex justify-between items-start mb-4">
          <div class="bg-gray-50 p-3 rounded-2xl">
            <span class="text-3xl grayscale opacity-50 block" v-if="e.status === 'Lulus'">Lulus</span>
            <span class="text-3xl grayscale opacity-50 block" v-else-if="e.status === 'Gagal'">Gagal</span>
            <span class="text-3xl grayscale opacity-50 block" v-else>Belajar</span>
          </div>
          <span :class="[
            'px-3 py-1 text-xs font-bold rounded-full border',
            e.status === 'Lulus' ? 'bg-green-50 text-green-700 border-green-200' : 
            (e.status === 'Gagal' ? 'bg-red-50 text-red-700 border-red-200' : 'bg-blue-50 text-blue-700 border-blue-200')
          ]">
            {{ e.status }}
          </span>
        </div>

        <h3 class="text-xl font-bold text-gray-900 mb-2 leading-tight flex-1">
          {{ trainings[e.training_id]?.title || 'Memuat...' }}
        </h3>
        
        <!-- Progress Bar -->
        <div class="mb-6">
          <div class="flex items-center text-xs text-gray-500 font-medium mb-4">
            <span>Terdaftar: {{ formatDate(e.enrolled_at) }}</span>
          </div>
          <div class="flex justify-between text-sm font-semibold mb-2">
            <span class="text-gray-600">Progres</span>
            <span :class="e.progress_percentage >= 100 ? 'text-green-600' : 'text-[var(--brown)]'">{{ e.progress_percentage }}%</span>
          </div>
          <div class="w-full bg-gray-100 h-3 rounded-full overflow-hidden shadow-inner">
            <div class="h-full rounded-full transition-all duration-1000 ease-out relative"
                 :class="e.progress_percentage >= 70 ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-[var(--brown)] to-[var(--gold)]'"
                 :style="`width: ${e.progress_percentage}%`">
                 <!-- Shine effect -->
                 <div class="absolute top-0 left-0 w-full h-full bg-white/20 animate-pulse"></div>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-3 mt-auto">
          <router-link :to="{ name: 'lms-training-detail', params: { id: e.training_id } }" 
             class="flex-1 text-center py-2.5 px-4 bg-gray-900 text-white text-sm font-semibold rounded-xl hover:bg-gray-800 transition-colors">
            Lanjut Belajar
          </router-link>
          
          <router-link v-if="e.status === 'Lulus'" :to="`/admin/enrollments/${e.id}/certificate`" class="flex-1 text-center py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-bold rounded-xl shadow-lg shadow-green-500/30 transition-all hover:-translate-y-0.5 relative overflow-hidden group">
              <span class="relative z-10 flex items-center justify-center gap-2">Sertifikat</span>
              <div class="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
            </router-link>
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
