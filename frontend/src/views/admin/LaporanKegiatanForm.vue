<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const editId = route.params.id ? Number(route.params.id) : null

const kegiatanOptions = ref([])
const existingLaporan = ref([])
const form = reactive({
  kegiatan_id: '',
  judul_laporan: '',
  ringkasan_pelaksanaan: '',
  jumlah_peserta: '',
  kendala: '',
  rekomendasi: '',
  tanggal_laporan: new Date().toISOString().slice(0, 10)
})
const fileLaporan = ref(null)

const errorMessage = ref('')
const infoMessage = ref('')
const saving = ref(false)
const uploading = ref(false)

const kegiatanTersedia = computed(() => {
  const sudahAda = new Set(existingLaporan.value.map((l) => l.kegiatan_id))
  return kegiatanOptions.value.filter((k) => !sudahAda.has(k.id))
})

onMounted(async () => {
  try {
    const [selesai, laporan] = await Promise.all([
      api.get('/admin/kegiatan', { params: { status: 'selesai' } }),
      api.get('/admin/laporan-kegiatan')
    ])
    kegiatanOptions.value = selesai.data
    existingLaporan.value = laporan.data
    if (editId) {
      const detail = await api.get(`/admin/laporan-kegiatan/${editId}`)
      const d = detail.data
      form.kegiatan_id = d.kegiatan_id
      form.judul_laporan = d.judul_laporan
      form.ringkasan_pelaksanaan = d.ringkasan_pelaksanaan
      form.jumlah_peserta = d.jumlah_peserta ?? ''
      form.kendala = d.kendala || ''
      form.rekomendasi = d.rekomendasi || ''
      form.tanggal_laporan = d.tanggal_laporan
      fileLaporan.value = d.file_laporan_url
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  infoMessage.value = ''
  if (!form.judul_laporan.trim() || !form.ringkasan_pelaksanaan.trim()) {
    errorMessage.value = 'Judul laporan dan ringkasan pelaksanaan wajib diisi.'
    return
  }
  if (editId) {
    saving.value = true
    try {
      const payload = {
        judul_laporan: form.judul_laporan.trim(),
        ringkasan_pelaksanaan: form.ringkasan_pelaksanaan.trim(),
        jumlah_peserta: form.jumlah_peserta ? Number(form.jumlah_peserta) : null,
        kendala: form.kendala.trim() || null,
        rekomendasi: form.rekomendasi.trim() || null,
        tanggal_laporan: form.tanggal_laporan
      }
      await api.put(`/admin/laporan-kegiatan/${editId}`, payload)
      router.push({ name: 'admin-laporan-kegiatan' })
    } catch (err) {
      errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan laporan.'
    } finally {
      saving.value = false
    }
    return
  }

  if (!form.kegiatan_id) {
    errorMessage.value = 'Pilih kegiatan yang sudah selesai.'
    return
  }
  if (!fileLaporan.value) {
    errorMessage.value = 'File laporan wajib diunggah.'
    return
  }
  saving.value = true
  try {
    const fd = new FormData()
    fd.append('kegiatan_id', Number(form.kegiatan_id))
    fd.append('judul_laporan', form.judul_laporan.trim())
    fd.append('ringkasan_pelaksanaan', form.ringkasan_pelaksanaan.trim())
    if (form.jumlah_peserta) fd.append('jumlah_peserta', Number(form.jumlah_peserta))
    if (form.kendala.trim()) fd.append('kendala', form.kendala.trim())
    if (form.rekomendasi.trim()) fd.append('rekomendasi', form.rekomendasi.trim())
    fd.append('tanggal_laporan', form.tanggal_laporan)
    fd.append('file', fileLaporan.value)
    const res = await api.post('/admin/laporan-kegiatan', fd)
    router.push({ name: 'admin-laporan-kegiatan' })
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal membuat laporan.'
  } finally {
    saving.value = false
  }
}

async function uploadFileBaru() {
  if (!editId || typeof fileLaporan.value !== 'object') return
  uploading.value = true
  errorMessage.value = ''
  try {
    const fd = new FormData()
    fd.append('file', fileLaporan.value)
    const res = await api.post(`/admin/laporan-kegiatan/${editId}/file`, fd)
    fileLaporan.value = res.data.file_laporan_url
    infoMessage.value = 'File laporan diperbarui.'
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengunggah file.'
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="page">
    <router-link to="/admin/laporan-kegiatan" class="back-link">Kembali ke Laporan Kegiatan</router-link>

    <div class="page-header">
      <div>
        <h2>{{ editId ? 'Edit Laporan Kegiatan' : 'Buat Laporan Kegiatan' }}</h2>
        <p class="greeting">Hanya kegiatan berstatus "selesai" yang bisa dibuatkan laporan.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>

    <form class="table-card" @submit.prevent="handleSubmit">
      <div v-if="!editId" class="form-group">
        <label>Kegiatan (Selesai)</label>
        <select v-model="form.kegiatan_id" required>
          <option value="">-- Pilih Kegiatan --</option>
          <option v-for="k in kegiatanTersedia" :key="k.id" :value="k.id">{{ k.judul }}</option>
        </select>
        <p v-if="!kegiatanTersedia.length" class="form-hint">
          Tidak ada kegiatan selesai yang belum punya laporan.
        </p>
      </div>
      <div v-else class="form-group">
        <label>Kegiatan</label>
        <input :value="kegiatanOptions.find((k) => k.id === form.kegiatan_id)?.judul || form.kegiatan_id" type="text" disabled />
      </div>

      <div class="form-group">
        <label>Judul Laporan</label>
        <input v-model="form.judul_laporan" type="text" placeholder="Judul laporan pelaksanaan" required />
      </div>

      <div class="form-group">
        <label>Ringkasan Pelaksanaan</label>
        <textarea v-model="form.ringkasan_pelaksanaan" rows="4" placeholder="Ringkasan jalannya kegiatan" required></textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Jumlah Peserta</label>
          <input v-model.number="form.jumlah_peserta" type="number" min="0" placeholder="Opsional" />
        </div>
        <div class="form-group">
          <label>Tanggal Laporan</label>
          <input v-model="form.tanggal_laporan" type="date" required />
        </div>
      </div>

      <div class="form-group">
        <label>Kendala</label>
        <textarea v-model="form.kendala" rows="2" placeholder="Kendala yang dihadapi (opsional)"></textarea>
      </div>

      <div class="form-group">
        <label>Rekomendasi</label>
        <textarea v-model="form.rekomendasi" rows="2" placeholder="Rekomendasi ke depan (opsional)"></textarea>
      </div>

      <div v-if="!editId" class="form-group">
        <label>File Laporan (wajib)</label>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" @change="fileLaporan = $event.target.files[0]" />
      </div>

      <div v-if="editId" class="form-group">
        <label>File Laporan</label>
        <a v-if="typeof fileLaporan === 'string' && fileLaporan" :href="`http://localhost:8000${fileLaporan}`" target="_blank" class="link-inline">
          Buka file saat ini
        </a>
        <input type="file" accept=".pdf,.jpg,.jpeg,.png,.docx" @change="fileLaporan = $event.target.files[0]" />
        <button
          v-if="typeof fileLaporan === 'object'"
          type="button"
          class="btn-submit"
          :disabled="uploading"
          @click="uploadFileBaru"
        >
          {{ uploading ? 'Mengunggah...' : 'Ganti File' }}
        </button>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn-small" @click="router.push({ name: 'admin-laporan-kegiatan' })">Batal</button>
        <button type="submit" class="btn-submit modal-submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : editId ? 'Simpan Perubahan' : 'Simpan Laporan' }}
        </button>
      </div>
    </form>
  </div>
</template>
