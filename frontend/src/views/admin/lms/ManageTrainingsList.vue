<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../../services/api'

const router = useRouter()
const trainings = ref([])
const loading = ref(true)

const showCreateModal = ref(false)
const newTraining = ref({
  title: '',
  description: '',
  passing_grade: 70
})

async function fetchTrainings() {
  loading.value = true
  try {
    const res = await api.get('/lms/trainings')
    // Handle paginated response structure if it exists, otherwise fallback to array
    trainings.value = res.data.items ? res.data.items : res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function createTraining() {
  try {
    const res = await api.post('/admin/lms/trainings', newTraining.value)
    showCreateModal.value = false
    router.push(`/admin/manage-trainings/${res.data.id}`)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal membuat pelatihan')
  }
}

async function deleteTraining(id) {
  if (!confirm('Apakah Anda yakin ingin menghapus pelatihan ini?')) return
  try {
    await api.delete(`/admin/lms/trainings/${id}`)
    await fetchTrainings()
  } catch (err) {
    alert('Gagal menghapus pelatihan')
  }
}

onMounted(() => {
  fetchTrainings()
})
</script>

<template>
  <div class="manage-trainings-content">
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
      <div>
        <h2>Kelola Pelatihan (LMS)</h2>
        <p class="subtitle">Buat dan atur program pelatihan, materi, serta kuis.</p>
      </div>
      <button class="btn-primary" @click="showCreateModal = true">+ Tambah Pelatihan</button>
    </div>

    <div v-if="loading" class="loading-state">Memuat data pelatihan...</div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Judul Pelatihan</th>
            <th>Passing Grade</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="trainings.length === 0">
            <td colspan="5" style="text-align: center; padding: 2rem;">Belum ada data pelatihan.</td>
          </tr>
          <tr v-for="t in trainings" :key="t.id">
            <td>#{{ t.id }}</td>
            <td>{{ t.title }}</td>
            <td>{{ t.passing_grade }}</td>
            <td><span :class="['badge', t.status === 'Published' ? 'badge-success' : 'badge-warning']">{{ t.status }}</span></td>
            <td>
              <router-link :to="`/admin/manage-trainings/${t.id}`" class="btn-secondary btn-sm" style="margin-right: 0.5rem;">Edit</router-link>
              <button class="btn-danger btn-sm" @click="deleteTraining(t.id)">Hapus</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Create Training -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Tambah Pelatihan Baru</h3>
        <form @submit.prevent="createTraining" style="margin-top: 1rem;">
          <div class="form-group">
            <label>Judul Pelatihan</label>
            <input type="text" v-model="newTraining.title" required />
          </div>
          <div class="form-group">
            <label>Deskripsi Singkat</label>
            <textarea v-model="newTraining.description" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Batas Nilai Kelulusan (Kuis)</label>
            <input type="number" v-model="newTraining.passing_grade" required min="0" max="100" />
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;">
            <button type="button" class="btn-secondary" @click="showCreateModal = false">Batal</button>
            <button type="submit" class="btn-primary">Buat & Lanjut</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
}
.data-table th, .data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}
.data-table th {
  background: #fafafa;
  font-weight: 600;
  color: #333;
}
.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.85rem;
}
.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-danger:hover {
  background-color: #c82333;
}
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}
.badge-success { background: #d4edda; color: #155724; }
.badge-warning { background: #fff3cd; color: #856404; }

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
</style>
