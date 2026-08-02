<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const currentUser = ref(null)
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const infoMessage = ref('')

const form = ref({
  judul: '',
  kategori: 'berita',
  deskripsi: '',
  tanggal_kegiatan: '',
  lokasi: ''
})

const kategoriOptions = [
  { value: 'berita', label: 'Berita' },
  { value: 'dokumentasi', label: 'Dokumentasi' },
  { value: 'agenda', label: 'Agenda' }
]

const tingkatLabels = {
  kwarcab: 'Kwarcab',
  kwaran: 'Kwaran',
  gudep: 'Gugus Depan'
}

const createdId = ref(null)

onMounted(async () => {
  try {
    const me = await api.get('/auth/me')
    currentUser.value = me.data
    const editId = route.query.edit
    if (editId) {
      const res = await api.get('/kontributor/hub-kegiatan/saya')
      const item = res.data.find((h) => h.id === Number(editId))
      if (item) {
        createdId.value = item.id
        form.value = {
          judul: item.judul,
          kategori: item.kategori,
          deskripsi: item.deskripsi,
          tanggal_kegiatan: item.tanggal_kegiatan,
          lokasi: item.lokasi
        }
      }
    }
  } catch (err) {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
    }
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  infoMessage.value = ''
  if (!form.value.judul.trim()) {
    errorMessage.value = 'Judul wajib diisi.'
    return
  }
  saving.value = true
  try {
    if (createdId.value) {
      await api.put(`/kontributor/hub-kegiatan/${createdId.value}`, form.value)
      infoMessage.value = 'Postingan berhasil diperbarui. Status tetap menunggu moderasi.'
    } else {
      const res = await api.post('/kontributor/hub-kegiatan', form.value)
      createdId.value = res.data.id
      infoMessage.value =
        'Postingan berhasil dikirim dan menunggu moderasi admin. Kamu masih bisa menambah foto/video di bawah.'
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan postingan.'
  } finally {
    saving.value = false
  }
}

const mediaFiles = ref([])
const uploading = ref(false)

async function handleUpload() {
  if (!mediaFiles.value.length || !createdId.value) return
  uploading.value = true
  errorMessage.value = ''
  infoMessage.value = ''
  try {
    for (const file of mediaFiles.value) {
      const tipe = file.type.startsWith('video/') ? 'video' : 'foto'
      const fd = new FormData()
      fd.append('file', file)
      await api.post(
        `/kontributor/hub-kegiatan/${createdId.value}/media?tipe=${tipe}`,
        fd
      )
    }
    mediaFiles.value = []
    infoMessage.value = 'Media berhasil diunggah.'
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail || 'Gagal mengunggah media. Maks 50MB per file.'
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="kontributor-page">
    <h1 class="page-title">Buat Postingan Hub Kegiatan</h1>
    <p class="page-subtitle">
      Postingan otomatis mewakili
      <strong v-if="currentUser">
        {{ tingkatLabels[currentUser.tingkat_wilayah] }} {{ currentUser.nama_wilayah || '' }}
      </strong>.
      Status awal: <span class="badge-status pending">Menunggu Moderasi</span>.
    </p>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="infoMessage" class="alert-success">{{ infoMessage }}</div>

    <form class="form-card" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="judul">Judul</label>
        <input
          id="judul"
          v-model="form.judul"
          type="text"
          placeholder="Contoh: Bakti Sosial di Kelurahan Coblong"
          required
        />
      </div>

      <div class="form-group">
        <label for="kategori">Kategori</label>
        <select id="kategori" v-model="form.kategori">
          <option v-for="k in kategoriOptions" :key="k.value" :value="k.value">
            {{ k.label }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="deskripsi">Deskripsi</label>
        <textarea
          id="deskripsi"
          v-model="form.deskripsi"
          rows="5"
          placeholder="Ceritakan kegiatan atau informasi ini..."
        ></textarea>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="tanggal_kegiatan">Tanggal Kegiatan</label>
          <input id="tanggal_kegiatan" v-model="form.tanggal_kegiatan" type="date" />
        </div>
        <div class="form-group">
          <label for="lokasi">Lokasi</label>
          <input id="lokasi" v-model="form.lokasi" type="text" placeholder="Contoh: Jl. Dago" />
        </div>
      </div>

      <div class="action-row">
        <button class="btn-submit" type="submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : createdId ? 'Simpan Perubahan' : 'Kirim Postingan' }}
        </button>
        <router-link to="/kontributor" class="btn-outline">Batal</router-link>
      </div>
    </form>

    <div v-if="createdId" class="form-card">
      <h2 class="card-title">Lampirkan Foto / Video</h2>
      <p class="text-muted">JPG/PNG untuk foto, MP4/WebM/MOV untuk video. Maks 50MB per file.</p>
      <input id="media" type="file" multiple accept="image/*,video/*" @change="mediaFiles = [...$event.target.files]" />
      <div v-if="mediaFiles.length" class="text-muted">{{ mediaFiles.length }} file dipilih.</div>
      <div class="action-row">
        <button class="btn-submit" type="button" :disabled="uploading" @click="handleUpload">
          {{ uploading ? 'Mengunggah...' : 'Unggah Media' }}
        </button>
      </div>
    </div>
  </div>
</template>
