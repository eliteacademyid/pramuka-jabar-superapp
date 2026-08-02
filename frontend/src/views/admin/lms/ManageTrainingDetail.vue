<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../../services/api'
import ActionModal from '../../../components/ActionModal.vue'

const route = useRoute()
const router = useRouter()
const trainingId = route.params.id

const activeTab = ref('info') // info, materials, quiz

const training = ref(null)
const materials = ref([])
const quiz = ref(null)
const questions = ref([])

const loading = ref(true)

// Modals
const showMaterialModal = ref(false)
const editingMaterialId = ref(null)
const newMaterial = ref({ title: '', content: '', media_url: '', order: 1 })

const showQuestionModal = ref(false)
const editingQuestionId = ref(null)
const newQuestion = ref({ question_text: '', options: '', correct_answer: '', score_weight: 10 })
const tempOptions = ref(['', '', '', ''])

const notification = ref({ show: false, type: 'success', title: '', message: '' })

function showNotification(type, title, message) {
  notification.value = { show: true, type, title, message }
}

async function loadData() {
  loading.value = true
  try {
    // Load training info
    const resT = await api.get('/lms/trainings')
    const allTrainings = resT.data.items ? resT.data.items : resT.data
    training.value = allTrainings.find(t => t.id == trainingId)

    if (!training.value) {
      showNotification('error', 'Gagal', 'Pelatihan tidak ditemukan')
      router.push('/admin/manage-trainings')
      return
    }

    // Load materials
    const resM = await api.get(`/lms/trainings/${trainingId}/materials`)
    materials.value = resM.data

    // Load Quiz
    try {
      const resQ = await api.get(`/lms/trainings/${trainingId}/quiz`)
      quiz.value = resQ.data
      
      const resQs = await api.get(`/lms/quizzes/${quiz.value.id}/questions`)
      questions.value = resQs.data
    } catch (e) {
      quiz.value = null
    }

  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function saveTrainingInfo() {
  try {
    await api.put(`/admin/lms/trainings/${trainingId}`, {
      title: training.value.title,
      description: training.value.description,
      passing_grade: training.value.passing_grade,
      status: training.value.status
    })
    showNotification('success', 'Berhasil', 'Informasi pelatihan berhasil disimpan')
  } catch(err) {
    showNotification('error', 'Gagal', 'Gagal menyimpan info pelatihan')
  }
}

function openAddMaterial() {
  editingMaterialId.value = null
  newMaterial.value = { title: '', content: '', media_url: '', order: materials.value.length + 1 }
  showMaterialModal.value = true
}

function openEditMaterial(m) {
  editingMaterialId.value = m.id
  newMaterial.value = { ...m }
  showMaterialModal.value = true
}

async function saveMaterial() {
  try {
    const payload = {
      ...newMaterial.value,
      training_id: Number(trainingId)
    }

    if (editingMaterialId.value) {
      await api.put(`/admin/lms/materials/${editingMaterialId.value}`, payload)
      showNotification('success', 'Berhasil', 'Materi berhasil diperbarui')
    } else {
      await api.post('/admin/lms/materials', payload)
      showNotification('success', 'Berhasil', 'Materi berhasil ditambahkan')
    }

    showMaterialModal.value = false
    editingMaterialId.value = null
    newMaterial.value = { title: '', content: '', media_url: '', order: 1 }
    await loadData()
  } catch(err) {
    showNotification('error', 'Gagal', 'Gagal menyimpan materi')
  }
}

async function deleteMaterial(id) {
  if(!confirm('Hapus materi ini?')) return
  try {
    await api.delete(`/admin/lms/materials/${id}`)
    await loadData()
    showNotification('success', 'Berhasil Dihapus', 'Materi berhasil dihapus dari pelatihan ini.')
  } catch (err) {
    showNotification('error', 'Gagal', 'Gagal menghapus materi.')
  }
}

async function createQuiz() {
  try {
    await api.post('/admin/lms/quizzes', {
      title: `Kuis: ${training.value.title}`,
      time_limit_minutes: 30,
      training_id: Number(trainingId)
    })
    await loadData()
    showNotification('success', 'Berhasil', 'Kuis berhasil diinisialisasi')
  } catch (err) {
    showNotification('error', 'Gagal', 'Gagal membuat kuis')
  }
}

function openAddQuestion() {
  editingQuestionId.value = null
  newQuestion.value = { question_text: '', options: '', correct_answer: '', score_weight: 10 }
  tempOptions.value = ['', '', '', '']
  showQuestionModal.value = true
}

function openEditQuestion(q) {
  editingQuestionId.value = q.id
  newQuestion.value = { ...q }
  try {
    const opts = JSON.parse(q.options)
    tempOptions.value = [...opts]
  } catch (e) {
    tempOptions.value = []
  }
  while (tempOptions.value.length < 4) tempOptions.value.push('')
  showQuestionModal.value = true
}

async function saveQuestion() {
  try {
    const validOptions = tempOptions.value.filter(o => o.trim() !== '')
    if (validOptions.length < 2) {
      return alert('Minimal 2 opsi jawaban!')
    }

    const payload = {
      quiz_id: quiz.value.id,
      question_text: newQuestion.value.question_text,
      options: JSON.stringify(validOptions),
      correct_answer: newQuestion.value.correct_answer,
      score_weight: newQuestion.value.score_weight
    }

    if (editingQuestionId.value) {
      await api.put(`/admin/lms/questions/${editingQuestionId.value}`, payload)
      showNotification('success', 'Berhasil', 'Soal berhasil diperbarui')
    } else {
      await api.post('/admin/lms/questions', payload)
      showNotification('success', 'Berhasil', 'Soal berhasil ditambahkan')
    }
    
    showQuestionModal.value = false
    editingQuestionId.value = null
    newQuestion.value = { question_text: '', options: '', correct_answer: '', score_weight: 10 }
    tempOptions.value = ['', '', '', '']
    await loadData()
  } catch(err) {
    showNotification('error', 'Gagal', 'Gagal menyimpan soal')
  }
}

async function deleteQuestion(id) {
  if(!confirm('Hapus soal ini?')) return
  try {
    await api.delete(`/admin/lms/questions/${id}`)
    await loadData()
    showNotification('success', 'Berhasil', 'Soal berhasil dihapus')
  } catch(err) {
    showNotification('error', 'Gagal', 'Gagal hapus soal')
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="manage-detail">
    <ActionModal
      :show="notification.show"
      :type="notification.type"
      :title="notification.title"
      :message="notification.message"
      @close="notification.show = false"
    />

    <div class="page-header" style="margin-bottom: 2rem;">
      <router-link to="/admin/manage-trainings" class="back-link">&larr; Kembali ke Daftar</router-link>
      <h2 style="margin-top: 1rem;">Kelola: {{ training?.title || 'Memuat...' }}</h2>
    </div>

    <div v-if="loading">Memuat data...</div>

    <div v-else>
      <div class="tabs">
        <button :class="{ active: activeTab === 'info' }" @click="activeTab = 'info'">Info Dasar</button>
        <button :class="{ active: activeTab === 'materials' }" @click="activeTab = 'materials'">Materi ({{ materials.length }})</button>
        <button :class="{ active: activeTab === 'quiz' }" @click="activeTab = 'quiz'">Kuis & Soal</button>
      </div>

      <div class="tab-content" v-if="activeTab === 'info'">
        <div class="card">
          <h3>Informasi Pelatihan</h3>
          <form @submit.prevent="saveTrainingInfo" class="mt-4">
            <div class="form-group">
              <label>Judul</label>
              <input type="text" v-model="training.title" required />
            </div>
            <div class="form-group">
              <label>Deskripsi</label>
              <textarea v-model="training.description" rows="4"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group" style="flex:1;">
                <label>Passing Grade</label>
                <input type="number" v-model="training.passing_grade" required />
              </div>
              <div class="form-group" style="flex:1;">
                <label>Status</label>
                <select v-model="training.status">
                  <option value="Draft">Draft</option>
                  <option value="Published">Published</option>
                </select>
              </div>
            </div>
            <button class="btn-primary" type="submit">Simpan Perubahan</button>
          </form>
        </div>
      </div>

      <div class="tab-content" v-if="activeTab === 'materials'">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3>Daftar Materi</h3>
          <button class="btn-primary" @click="openAddMaterial">+ Tambah Materi</button>
        </div>
        
        <div v-if="materials.length === 0" class="empty-state">Belum ada materi untuk pelatihan ini.</div>
        
        <div v-for="m in materials" :key="m.id" class="card list-item">
          <div class="item-info">
            <span class="badge" style="background:#eee; color:#333; margin-right: 1rem;">Urutan: {{ m.order }}</span>
            <strong>{{ m.title }}</strong>
          </div>
          <div class="item-actions">
            <button class="btn-secondary btn-sm" @click="openEditMaterial(m)" style="margin-right: 0.5rem;">Edit</button>
            <button class="btn-danger btn-sm" @click="deleteMaterial(m.id)">Hapus</button>
          </div>
        </div>
      </div>

      <div class="tab-content" v-if="activeTab === 'quiz'">
        <div v-if="!quiz" class="empty-state" style="text-align: center;">
          <p>Pelatihan ini belum memiliki Kuis Evaluasi.</p>
          <button class="btn-primary" @click="createQuiz" style="margin-top: 1rem;">Inisialisasi Kuis</button>
        </div>

        <div v-else>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3>Soal Kuis Evaluasi</h3>
            <button class="btn-primary" @click="openAddQuestion">+ Tambah Soal</button>
          </div>

          <div v-if="questions.length === 0" class="empty-state">Belum ada soal. Tambahkan soal pertama Anda.</div>

          <div v-for="(q, idx) in questions" :key="q.id" class="card question-card">
            <div class="q-header">
              <strong>{{ idx + 1 }}. {{ q.question_text }}</strong>
              <div>
                <button class="btn-secondary btn-sm" @click="openEditQuestion(q)" style="margin-right: 0.5rem;">Edit</button>
                <button class="btn-danger btn-sm" @click="deleteQuestion(q.id)">Hapus</button>
              </div>
            </div>
            <ul class="q-options">
              <li v-for="opt in JSON.parse(q.options)" :key="opt" :class="{ 'correct': opt === q.correct_answer }">
                {{ opt }}
                <span v-if="opt === q.correct_answer" class="badge badge-success" style="margin-left: 0.5rem;">Benar</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

    </div>


    <!-- Material Modal -->
    <div v-if="showMaterialModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ editingMaterialId ? 'Edit Materi' : 'Tambah Materi' }}</h3>
        <form @submit.prevent="saveMaterial" style="margin-top: 1rem;">
          <div class="form-group">
            <label>Judul Materi</label>
            <input type="text" v-model="newMaterial.title" required />
          </div>
          <div class="form-group">
            <label>Konten Teks (Opsional)</label>
            <textarea v-model="newMaterial.content" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>URL Media / Video (Opsional)</label>
            <input type="url" v-model="newMaterial.media_url"
                   placeholder="https://youtube.com/watch?v=... atau https://drive.google.com/..." />
            <small style="color: #9ca3af; font-size: 0.75rem; margin-top: 0.25rem; display:block;">
              Mendukung: YouTube, Google Drive, file .mp4, .pdf, atau URL lainnya
            </small>
          </div>
          <div class="form-group">
            <label>Urutan Penampilan</label>
            <input type="number" v-model="newMaterial.order" required />
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;">
            <button type="button" class="btn-secondary" @click="showMaterialModal = false">Batal</button>
            <button type="submit" class="btn-primary">Simpan</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showQuestionModal" class="modal-overlay">
      <div class="modal-content" style="max-width: 600px;">
        <h3>{{ editingQuestionId ? 'Edit Soal Pilihan Ganda' : 'Tambah Soal Pilihan Ganda' }}</h3>
        <form @submit.prevent="saveQuestion" style="margin-top: 1rem;">
          <div class="form-group">
            <label>Pertanyaan</label>
            <textarea v-model="newQuestion.question_text" rows="2" required></textarea>
          </div>
          
          <label>Opsi Jawaban (Isi minimal 2)</label>
          <div class="options-grid">
            <div class="form-group" v-for="(opt, i) in tempOptions" :key="i">
              <input type="text" v-model="tempOptions[i]" :placeholder="'Opsi ' + (i+1)" />
            </div>
          </div>

          <div class="form-group mt-3">
            <label>Kunci Jawaban Tepat (Copy-paste persis dari salah satu opsi)</label>
            <input type="text" v-model="newQuestion.correct_answer" required />
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem;">
            <button type="button" class="btn-secondary" @click="showQuestionModal = false">Batal</button>
            <button type="submit" class="btn-primary">Simpan Soal</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style scoped>
.back-link {
  color: var(--brown);
  text-decoration: none;
  font-weight: 500;
}
.back-link:hover { text-decoration: underline; }

.tabs {
  display: flex;
  gap: 1rem;
  border-bottom: 2px solid #eee;
  margin-bottom: 2rem;
}
.tabs button {
  background: none;
  border: none;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
}
.tabs button.active {
  color: var(--brown);
  border-bottom-color: var(--brown);
}
.tabs button:hover:not(.active) {
  color: #333;
}

.card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 1rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}
.mt-4 { margin-top: 1.5rem; }
.mt-3 { margin-top: 1rem; }

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.empty-state {
  background: #f9f9f9;
  padding: 3rem;
  text-align: center;
  border-radius: 8px;
  color: #666;
}

.btn-sm { padding: 0.35rem 0.75rem; font-size: 0.85rem; }
.btn-danger { background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; }

.question-card {
  background: #fafafa;
  border-left: 4px solid var(--primary);
}
.q-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}
.q-options {
  list-style-type: lower-alpha;
  padding-left: 1.5rem;
  margin: 0;
}
.q-options li {
  padding: 0.25rem 0;
  color: #444;
}
.q-options li.correct {
  font-weight: 600;
  color: #155724;
}

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white; padding: 2rem; border-radius: 8px;
  width: 90%; max-width: 500px;
}
.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
</style>
