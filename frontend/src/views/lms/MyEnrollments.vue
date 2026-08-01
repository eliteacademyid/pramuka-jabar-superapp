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
  <div class="dashboard-content">
    <div class="page-header">
      <h2>Riwayat Pelatihan Saya</h2>
    </div>

    <div v-if="loading" class="empty-row">Memuat data...</div>
    <div v-else-if="error" class="alert-error">{{ error }}</div>
    <div v-else-if="enrollments.length === 0" class="empty-row">
      Anda belum mengikuti pelatihan apa pun.
    </div>

    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>Judul Pelatihan</th>
            <th>Tanggal Daftar</th>
            <th>Progres (%)</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in enrollments" :key="e.id">
            <td style="font-weight: 600;">
              {{ trainings[e.training_id]?.title || 'Memuat...' }}
            </td>
            <td>{{ formatDate(e.enrolled_at) }}</td>
            <td>
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="flex: 1; height: 8px; background: #eadfd3; border-radius: 4px; overflow: hidden;">
                  <div :style="{ width: e.progress_percentage + '%', height: '100%', background: e.progress_percentage >= 70 ? '#1e7d34' : 'var(--brown)' }"></div>
                </div>
                <span style="font-size: 0.85rem; font-weight: 600;">{{ e.progress_percentage }}%</span>
              </div>
            </td>
            <td>
              <span class="badge" 
                    :class="e.status === 'Lulus' ? 'badge-admin' : (e.status === 'Enrolled' ? 'badge-staff' : '')"
                    :style="e.status === 'Lulus' ? 'background: #1e7d34;' : (e.status === 'Gagal' ? 'background: var(--maroon);' : '')">
                {{ e.status }}
              </span>
            </td>
            <td>
              <router-link :to="{ name: 'lms-training-detail', params: { id: e.training_id } }" class="btn-small">
                Lanjut Belajar
              </router-link>
              <router-link v-if="e.status === 'Lulus'" :to="{ name: 'lms-certificate', params: { id: e.id } }" class="btn-small" style="color: #1e7d34; border-color: #1e7d34;">
                📄 Sertifikat
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
