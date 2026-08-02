<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

let editId = route.params.id ? Number(route.params.id) : null

const klasifikasi = ref([])
const form = reactive({
  tanggal_surat: '',
  tujuan: '',
  perihal: '',
  klasifikasi_id: '',
  sifat: 'biasa',
  isi_ringkas: ''
})

const sifatList = ['biasa', 'penting', 'segera', 'rahasia']

const statusLabels = {
  draft: 'Draft',
  menunggu_ttd: 'Menunggu TTD',
  terkirim: 'Terkirim'
}

const errorMessage = ref('')
const infoMessage = ref('')
const saving = ref(false)

const fileSurat = ref(null)
const uploading = ref(false)
const nomorSurat = ref(null)
const statusSekarang = ref(null)

onMounted(async () => {
  try {
    const res = await api.get('/admin/klasifikasi-surat')
    klasifikasi.value = res.data
    if (editId) {
      const detail = await api.get(`/admin/surat-keluar/${editId}`)
      const d = detail.data
      nomorSurat.value = d.nomor_surat
      statusSekarang.value = d.status
      form.tanggal_surat = d.tanggal_surat
      form.tujuan = d.tujuan
      form.perihal = d.perihal
      form.klasifikasi_id = d.klasifikasi_id
      form.sifat = d.sifat
      form.isi_ringkas = d.isi_ringkas || ''
      fileSurat.value = d.file_surat_url
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  infoMessage.value = ''
  if (!form.tujuan.trim() || !form.perihal.trim() || !form.klasifikasi_id) {
    errorMessage.value = 'Tujuan, perihal, dan klasifikasi wajib diisi.'
    return
  }
  saving.value = true
  try {
    if (editId) {
      await api.put(`/admin/surat-keluar/${editId}`, form)
      infoMessage.value = 'Data surat berhasil diperbarui.'
      const detail = await api.get(`/admin/surat-keluar/${editId}`)
      statusSekarang.value = detail.data.status
      nomorSurat.value = detail.data.nomor_surat
    } else {
      const res = await api.post('/admin/surat-keluar', form)
      await router.replace({ name: 'admin-surat-keluar-edit', params: { id: res.data.id } })
      editId = res.data.id
      statusSekarang.value = 'draft'
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan surat.'
  } finally {
    saving.value = false
  }
}

async function handleUploadFile() {
  if (!editId || typeof fileSurat.value !== 'object') return
  uploading.value = true
  errorMessage.value = ''
  try {
    const fd = new FormData()
    fd.append('file', fileSurat.value)
    const res = await api.post(`/admin/surat-keluar/${editId}/file`, fd)
    fileSurat.value = res.data.file_surat_url
    infoMessage.value = 'File surat berhasil diunggah.'
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengunggah file.'
  } finally {
    uploading.value = false
  }
}

async function ubahStatus(statusBaru) {
  errorMessage.value = ''
  infoMessage.value = ''
  if (statusBaru === 'terkirim' && typeof fileSurat.value === 'object') {
    await handleUploadFile()
  }
  try {
    await api.patch(`/admin/surat-keluar/${editId}/status`, { status: statusBaru })
    statusSekarang.value = statusBaru
    infoMessage.value = `Status berubah menjadi "${statusLabels[statusBaru]}".`
    const detail = await api.get(`/admin/surat-keluar/${editId}`)
    nomorSurat.value = detail.data.nomor_surat
    fileSurat.value = detail.data.file_surat_url
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengubah status.'
  }
}

async function hapusSurat() {
  if (!window.confirm('Hapus surat keluar ini? Hanya bisa saat status Draft.')) return
  try {
    await api.delete(`/admin/surat-keluar/${editId}`)
    router.push({ name: 'admin-surat-keluar' })
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menghapus surat.'
  }
}
</script>

<template>
  <div class="page">
    <router-link to="/admin/surat-keluar" class="back-link">Kembali ke Surat Keluar</router-link>

    <div class="page-header">
      <div>
        <h2>{{ editId ? 'Detail Surat Keluar' : 'Buat Surat Keluar' }}</h2>
        <p class="greeting">
          Nomor: <strong>{{ nomorSurat || 'Belum digenerate (draft)' }}</strong> | Status:
          <span class="badge-sk" :class="`status-${statusSekarang || 'draft'}`">
            {{ statusLabels[statusSekarang || 'draft'] }}
          </span>
        </p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>

    <form class="table-card" @submit.prevent="handleSubmit">
      <div class="form-row">
        <div class="form-group">
          <label>Tanggal Surat</label>
          <input v-model="form.tanggal_surat" type="date" required />
        </div>
        <div class="form-group">
          <label>Klasifikasi</label>
          <select v-model="form.klasifikasi_id" required>
            <option value="">-- Pilih --</option>
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
        <label>Tujuan</label>
        <input v-model="form.tujuan" type="text" placeholder="Instansi / orang tujuan" required />
      </div>

      <div class="form-group">
        <label>Perihal</label>
        <input v-model="form.perihal" type="text" placeholder="Perihal surat" required />
      </div>

      <div class="form-group">
        <label>Isi Ringkas</label>
        <textarea v-model="form.isi_ringkas" rows="4" placeholder="Ringkasan isi surat (opsional)"></textarea>
      </div>

      <div v-if="statusSekarang !== 'terkirim'" class="modal-actions">
        <button type="submit" class="btn-submit modal-submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : editId ? 'Simpan Perubahan' : 'Simpan Draft' }}
        </button>
        <button v-if="editId && statusSekarang === 'draft'" type="button" class="btn-danger" @click="hapusSurat">
          Hapus
        </button>
      </div>
    </form>

    <div v-if="editId" class="table-card">
      <h3 class="card-title">File Surat</h3>
      <p class="greeting">PDF, JPG, PNG, DOCX. Maks 10 MB. Wajib diisi sebelum status Terkirim.</p>
      <div class="action-row">
        <a v-if="typeof fileSurat === 'string' && fileSurat" :href="`http://localhost:8000${fileSurat}`" target="_blank" class="link-inline">
          Buka file surat
        </a>
        <input
          v-if="statusSekarang !== 'terkirim'"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.docx"
          @change="fileSurat = $event.target.files[0]"
        />
        <button
          v-if="statusSekarang !== 'terkirim' && typeof fileSurat === 'object'"
          class="btn-submit"
          :disabled="uploading"
          @click="handleUploadFile"
        >
          {{ uploading ? 'Mengunggah...' : 'Unggah File' }}
        </button>
      </div>
    </div>

    <div v-if="editId && statusSekarang !== 'terkirim'" class="table-card">
      <h3 class="card-title">Alur Status</h3>
      <p class="greeting">Draft → Menunggu TTD → Terkirim. Nomor surat digenerate saat menuju Menunggu TTD.</p>
      <div class="action-row">
        <button
          v-if="statusSekarang === 'draft'"
          class="btn-primary btn-add"
          @click="ubahStatus('menunggu_ttd')"
        >
          Kirim ke Menunggu TTD
        </button>
        <button
          v-if="statusSekarang === 'menunggu_ttd'"
          class="btn-primary btn-add"
          @click="ubahStatus('terkirim')"
        >
          Tandai Terkirim
        </button>
      </div>
    </div>
  </div>
</template>
