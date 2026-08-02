<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const editId = route.query.edit ? Number(route.query.edit) : null

const klasifikasi = ref([])
const form = reactive({
  nomor_surat_asal: '',
  tanggal_surat: '',
  tanggal_diterima: '',
  pengirim: '',
  perihal: '',
  klasifikasi_id: '',
  sifat: 'biasa'
})

const sifatList = ['biasa', 'penting', 'segera', 'rahasia']

const errorMessage = ref('')
const infoMessage = ref('')
const saving = ref(false)

const scanFile = ref(null)
const uploading = ref(false)

const nomorAgenda = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/admin/klasifikasi-surat')
    klasifikasi.value = res.data
    if (editId) {
      const detail = await api.get(`/admin/surat-masuk/${editId}`)
      const d = detail.data
      nomorAgenda.value = d.nomor_agenda
      form.nomor_surat_asal = d.nomor_surat_asal || ''
      form.tanggal_surat = d.tanggal_surat
      form.tanggal_diterima = d.tanggal_diterima
      form.pengirim = d.pengirim
      form.perihal = d.perihal
      form.klasifikasi_id = d.klasifikasi_id
      form.sifat = d.sifat
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  infoMessage.value = ''
  if (!form.pengirim.trim() || !form.perihal.trim() || !form.klasifikasi_id) {
    errorMessage.value = 'Pengirim, perihal, dan klasifikasi wajib diisi.'
    return
  }
  saving.value = true
  try {
    if (editId) {
      await api.put(`/admin/surat-masuk/${editId}`, form)
      infoMessage.value = 'Surat masuk berhasil diperbarui.'
    } else {
      const res = await api.post('/admin/surat-masuk', form)
      await router.push({ name: 'admin-surat-masuk-detail', params: { id: res.data.id } })
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan surat masuk.'
  } finally {
    saving.value = false
  }
}

async function handleUploadScan() {
  if (!scanFile.value || !editId) return
  uploading.value = true
  errorMessage.value = ''
  try {
    const fd = new FormData()
    fd.append('file', scanFile.value)
    await api.post(`/admin/surat-masuk/${editId}/scan`, fd)
    infoMessage.value = 'File scan berhasil diunggah.'
    scanFile.value = null
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengunggah scan.'
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>{{ editId ? `Edit Surat Masuk ${nomorAgenda}` : 'Input Surat Masuk' }}</h2>
        <p class="greeting">Nomor agenda digenerate otomatis oleh sistem.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>

    <form class="table-card" @submit.prevent="handleSubmit">
      <div class="form-row">
        <div class="form-group">
          <label>Nomor Surat Asal</label>
          <input v-model="form.nomor_surat_asal" type="text" placeholder="Contoh: 005/PAN/2026" />
        </div>
        <div class="form-group">
          <label>Tanggal Surat</label>
          <input v-model="form.tanggal_surat" type="date" required />
        </div>
        <div class="form-group">
          <label>Tanggal Diterima</label>
          <input v-model="form.tanggal_diterima" type="date" required />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Pengirim</label>
          <input v-model="form.pengirim" type="text" placeholder="Nama instansi / orang" required />
        </div>
        <div class="form-group">
          <label>Klasifikasi</label>
          <select v-model="form.klasifikasi_id" required>
            <option value="">-- Pilih Klasifikasi --</option>
            <option v-for="k in klasifikasi" :key="k.id" :value="k.id">{{ k.kode }} {{ k.nama_klasifikasi }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>Sifat</label>
          <select v-model="form.sifat">
            <option v-for="s in sifatList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Perihal</label>
        <input v-model="form.perihal" type="text" placeholder="Perihal surat" required />
      </div>

      <div class="modal-actions">
        <button type="button" class="btn-small" @click="router.push({ name: 'admin-surat-masuk' })">Batal</button>
        <button type="submit" class="btn-submit modal-submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : editId ? 'Simpan Perubahan' : 'Simpan Surat' }}
        </button>
      </div>
    </form>

    <div v-if="editId" class="table-card">
      <h3 class="card-title">File Scan Surat</h3>
      <p class="greeting">PDF, JPG, PNG, DOCX. Maks 10 MB.</p>
      <div class="action-row">
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" @change="scanFile = $event.target.files[0]" />
        <button class="btn-submit" :disabled="!scanFile || uploading" @click="handleUploadScan">
          {{ uploading ? 'Mengunggah...' : 'Unggah Scan' }}
        </button>
      </div>
    </div>
  </div>
</template>
