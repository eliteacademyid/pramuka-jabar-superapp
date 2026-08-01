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
  <div class="dashboard-content">
    <div v-if="loading" class="empty-row">Memuat detail pelatihan...</div>
    <div v-else-if="error" class="alert-error">{{ error }}</div>
    <div v-else-if="training">
      <div class="page-header" style="flex-direction: column; gap: 0.5rem; align-items: flex-start;">
        <router-link to="/admin/trainings" class="back-link">← Kembali ke Daftar Pelatihan</router-link>
        <h2 style="font-size: 2rem; color: var(--brown); margin-top: 1rem;">{{ training.title }}</h2>
        <span class="badge" :class="training.status === 'Published' ? 'badge-admin' : 'badge-staff'">{{ training.status }}</span>
      </div>

      <div class="stat-card" style="margin-bottom: 2rem; box-shadow: none;">
        <p style="font-size: 1.05rem; margin-bottom: 1.5rem;">{{ training.description }}</p>
        
        <div v-if="!isEnrolled" style="text-align: center; padding: 2rem; background: #faf6f0; border-radius: 8px;">
          <h3 style="margin-bottom: 1rem; color: var(--brown);">Tertarik mengikuti pelatihan ini?</h3>
          <button class="btn-primary" @click="enroll" :disabled="enrolling">
            {{ enrolling ? 'Mendaftar...' : 'Daftar Sekarang' }}
          </button>
        </div>
      </div>

      <div v-if="isEnrolled">
        <h3 style="color: var(--brown); margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid var(--gold);">
          Modul Pembelajaran
        </h3>
        
        <div v-if="materials.length === 0" class="empty-row">
          Belum ada materi untuk pelatihan ini.
        </div>
        
        <div v-else style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem;">
          <div v-for="(mat, idx) in materials" :key="mat.id" class="table-card" style="padding: 1.5rem; border-radius: 8px;">
            <h4 style="font-size: 1.2rem; color: var(--maroon); margin-bottom: 0.5rem;">
              {{ idx + 1 }}. {{ mat.title }}
            </h4>
            <div style="white-space: pre-wrap; font-size: 0.95rem; color: #444; margin-bottom: 1rem;">{{ mat.content }}</div>
            <a v-if="mat.media_url" :href="mat.media_url" target="_blank" style="color: var(--gold); font-weight: 600; text-decoration: none;">
              🔗 Buka Tautan Media Pendukung
            </a>
          </div>
        </div>
        
        <div v-if="hasQuiz" style="text-align: center; margin-top: 3rem; padding: 2rem; border: 2px dashed var(--gold); border-radius: 12px;">
          <h3 style="margin-bottom: 1rem; color: var(--brown);">Sudah selesai mempelajari materi?</h3>
          <router-link :to="{ name: 'lms-training-quiz', params: { id: training.id } }" class="btn-primary" style="background: var(--brown);">
            Mulai Evaluasi / Kuis
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
