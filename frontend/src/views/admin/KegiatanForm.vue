<script setup>
import { reactive, ref, watch } from 'vue'
import api from '../../services/api'

const props = defineProps({
  initial: { type: Object, default: null },
  isEdit: { type: Boolean, default: false },
  programKerja: { type: Array, default: () => [] },
  save: { type: Function, required: true }
})

const emit = defineEmits(['saved', 'cancel'])

const statusList = ['rencana', 'berjalan', 'selesai', 'dibatalkan']
const tipeList = ['notulen', 'absensi', 'dokumentasi', 'lainnya']
const allowedExt = ['pdf', 'jpg', 'jpeg', 'png', 'docx']
const maxMb = 10

const saving = ref(false)
const formError = ref('')
const uploadError = ref('')
const uploading = ref(false)
const uploadTipe = ref('lainnya')
const selectedFiles = ref([])
const dokumen = ref([])

const form = reactive({
  judul: '',
  deskripsi: '',
  tanggal_mulai: '',
  tanggal_selesai: '',
  waktu: '',
  lokasi: '',
  penanggung_jawab: '',
  program_kerja_id: '',
  status: 'rencana',
  untuk_publik: false,
  catatan_pelaksanaan: ''
})

watch(
  () => props.initial,
  (val) => {
    Object.assign(form, {
      judul: val?.judul ?? '',
      deskripsi: val?.deskripsi ?? '',
      tanggal_mulai: val?.tanggal_mulai ?? '',
      tanggal_selesai: val?.tanggal_selesai ?? '',
      waktu: val?.waktu ?? '',
      lokasi: val?.lokasi ?? '',
      penanggung_jawab: val?.penanggung_jawab ?? '',
      program_kerja_id: val?.program_kerja_id ?? '',
      status: val?.status ?? 'rencana',
      untuk_publik: val?.untuk_publik ?? false,
      catatan_pelaksanaan: val?.catatan_pelaksanaan ?? ''
    })
    dokumen.value = val?.dokumen ?? []
    selectedFiles.value = []
    uploadError.value = ''
    formError.value = ''
  },
  { immediate: true }
)

function validate() {
  if (!form.judul.trim()) return 'Judul wajib diisi.'
  if (!form.tanggal_mulai) return 'Tanggal mulai wajib diisi.'
  if (
    form.tanggal_selesai &&
    new Date(form.tanggal_selesai) < new Date(form.tanggal_mulai)
  ) {
    return 'Tanggal selesai tidak boleh lebih awal dari tanggal mulai.'
  }
  return ''
}

function onFileChange(event) {
  selectedFiles.value = Array.from(event.target.files || [])
}

function validateFiles() {
  for (const f of selectedFiles.value) {
    const ext = (f.name.split('.').pop() || '').toLowerCase()
    if (!allowedExt.includes(ext)) {
      return `"${f.name}" tidak diizinkan. Gunakan pdf, jpg, png, atau docx.`
    }
    if (f.size > maxMb * 1024 * 1024) {
      return `"${f.name}" melebihi ${maxMb} MB.`
    }
  }
  return ''
}

async function uploadFiles() {
  const kegiatanId = props.initial?.id
  if (!kegiatanId) {
    uploadError.value = 'Simpan kegiatan terlebih dahulu sebelum upload lampiran.'
    return
  }
  uploadError.value = validateFiles()
  if (uploadError.value) return
  uploading.value = true
  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post(
        `/admin/kegiatan/${kegiatanId}/dokumen?tipe=${uploadTipe.value}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      dokumen.value.push(res.data)
    }
    selectedFiles.value = []
    uploadError.value = ''
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Gagal upload dokumen.'
  } finally {
    uploading.value = false
  }
}

async function removeDokumen(dok) {
  if (!window.confirm(`Hapus dokumen "${dok.nama_file}"?`)) return
  try {
    await api.delete(`/admin/kegiatan/${props.initial.id}/dokumen/${dok.id}`)
    dokumen.value = dokumen.value.filter((d) => d.id !== dok.id)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus dokumen.')
  }
}

async function submit() {
  formError.value = validate()
  if (formError.value) return
  saving.value = true
  try {
    const payload = {
      judul: form.judul.trim(),
      deskripsi: form.deskripsi || null,
      tanggal_mulai: form.tanggal_mulai,
      tanggal_selesai: form.tanggal_selesai || null,
      waktu: form.waktu || null,
      lokasi: form.lokasi || null,
      penanggung_jawab: form.penanggung_jawab || null,
      program_kerja_id: form.program_kerja_id ? Number(form.program_kerja_id) : null,
      status: form.status,
      untuk_publik: form.untuk_publik,
      catatan_pelaksanaan:
        form.status === 'selesai' && form.catatan_pelaksanaan
          ? form.catatan_pelaksanaan
          : null
    }
    const created = await props.save(payload)
    emit('saved', created)
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan data.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <form class="modal-card kegiatan-form" @submit.prevent="submit">
    <h3>{{ isEdit ? 'Edit Kegiatan' : 'Tambah Kegiatan' }}</h3>

    <div v-if="formError" class="alert-error">{{ formError }}</div>

    <div class="form-grid">
      <div class="form-group form-grid-full">
        <label for="kg-judul">Judul Kegiatan</label>
        <input id="kg-judul" v-model="form.judul" type="text" required />
      </div>

      <div class="form-group">
        <label for="kg-mulai">Tanggal Mulai</label>
        <input id="kg-mulai" v-model="form.tanggal_mulai" type="date" required />
      </div>
      <div class="form-group">
        <label for="kg-selesai">Tanggal Selesai</label>
        <input id="kg-selesai" v-model="form.tanggal_selesai" type="date" />
      </div>
      <div class="form-group">
        <label for="kg-waktu">Waktu</label>
        <input id="kg-waktu" v-model="form.waktu" type="text" placeholder="08.00 - 12.00 WIB" />
      </div>
      <div class="form-group">
        <label for="kg-lokasi">Lokasi</label>
        <input id="kg-lokasi" v-model="form.lokasi" type="text" />
      </div>
      <div class="form-group">
        <label for="kg-pj">Penanggung Jawab</label>
        <input id="kg-pj" v-model="form.penanggung_jawab" type="text" />
      </div>
      <div class="form-group">
        <label for="kg-pk">Program Kerja Terkait (opsional)</label>
        <select id="kg-pk" v-model="form.program_kerja_id">
          <option value="">- Tidak terkait -</option>
          <option v-for="p in programKerja" :key="p.id" :value="p.id">{{ p.judul }}</option>
        </select>
      </div>
      <div class="form-group form-grid-full">
        <label for="kg-deskripsi">Deskripsi</label>
        <textarea id="kg-deskripsi" v-model="form.deskripsi" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label for="kg-status">Status</label>
        <select id="kg-status" v-model="form.status">
          <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div v-if="form.status === 'selesai'" class="form-group form-grid-full">
        <label for="kg-catatan">Catatan Pelaksanaan (notulen singkat)</label>
        <textarea id="kg-catatan" v-model="form.catatan_pelaksanaan" rows="3"></textarea>
      </div>
      <div class="form-group checkbox-group form-grid-full">
        <label>
          <input v-model="form.untuk_publik" type="checkbox" />
          Tampilkan di kalender/agenda publik (beranda)
        </label>
        <p class="form-hint">Centang hanya untuk kegiatan yang memang untuk masyarakat luas, bukan rapat/agenda internal.</p>
      </div>
    </div>

    <div v-if="initial && initial.id" class="upload-section">
      <h4>Lampiran Dokumen</h4>

      <div v-if="dokumen.length" class="doc-list">
        <div v-for="d in dokumen" :key="d.id" class="doc-item">
          <a :href="d.file_url" target="_blank" rel="noopener" class="doc-name">
            {{ d.nama_file }}
          </a>
          <span class="doc-tipe">{{ d.tipe }}</span>
          <button class="btn-small btn-danger" @click="removeDokumen(d)">Hapus</button>
        </div>
      </div>
      <p v-else class="greeting">Belum ada lampiran.</p>

      <div v-if="uploadError" class="alert-error">{{ uploadError }}</div>

      <div class="upload-row">
        <input id="kg-file" type="file" multiple @change="onFileChange" />
        <select v-model="uploadTipe">
          <option v-for="t in tipeList" :key="t" :value="t">{{ t }}</option>
        </select>
        <button type="button" class="btn-small" :disabled="uploading || selectedFiles.length === 0" @click="uploadFiles">
          {{ uploading ? 'Mengunggah...' : 'Upload' }}
        </button>
      </div>
      <p class="upload-hint">
        Tipe diizinkan: pdf, jpg, png, docx (maks {{ maxMb }} MB per file)
      </p>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn-small" @click="emit('cancel')">Batal</button>
      <button type="submit" class="btn-submit modal-submit" :disabled="saving">
        {{ saving ? 'Menyimpan...' : 'Simpan' }}
      </button>
    </div>
  </form>
</template>
