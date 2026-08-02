<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()
const isEdit = !!route.params.id

const kategori = ref([])
const form = ref({
  nama_produk: '',
  kategori_id: '',
  harga: '',
  stok: '',
  deskripsi: '',
  status: 'aktif'
})
const fotoUrl = ref('')
const file = ref(null)
const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const resKat = await api.get('/penjual/kategori')
    kategori.value = resKat.data

    if (isEdit) {
      const res = await api.get(`/penjual/produk/${route.params.id}`)
      const p = res.data
      form.value = {
        nama_produk: p.nama_produk,
        kategori_id: String(p.kategori_id),
        harga: p.harga,
        stok: p.stok,
        deskripsi: p.deskripsi || '',
        status: p.status
      }
      fotoUrl.value = p.foto_url
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
})

function onFileChange(e) {
  file.value = e.target.files[0] || null
}

async function submit() {
  errorMessage.value = ''
  if (!form.value.nama_produk.trim()) {
    errorMessage.value = 'Nama produk wajib diisi.'
    return
  }
  if (!form.value.kategori_id) {
    errorMessage.value = 'Pilih kategori produk.'
    return
  }
  const harga = parseInt(form.value.harga, 10)
  const stok = parseInt(form.value.stok, 10)
  if (isNaN(harga) || harga <= 0) {
    errorMessage.value = 'Harga harus angka lebih dari 0.'
    return
  }
  if (isNaN(stok) || stok < 0) {
    errorMessage.value = 'Stok harus angka.'
    return
  }

  saving.value = true
  try {
    const fd = new FormData()
    fd.append('nama_produk', form.value.nama_produk.trim())
    fd.append('kategori_id', form.value.kategori_id)
    fd.append('harga', String(harga))
    fd.append('stok', String(stok))
    fd.append('deskripsi', form.value.deskripsi.trim() || '')
    if (!isEdit) {
      fd.append('status', form.value.status)
      if (!file.value) {
        errorMessage.value = 'Foto produk wajib diunggah.'
        saving.value = false
        return
      }
      fd.append('file', file.value)
    } else {
      fd.append('status', form.value.status)
      if (file.value) fd.append('file', file.value)
    }

    if (isEdit) await api.put(`/penjual/produk/${route.params.id}`, fd)
    else await api.post('/penjual/produk', fd)
    router.push('/penjual/produk')
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan produk.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="penjual-page">
    <div class="page-header">
      <h1>{{ isEdit ? 'Edit Produk' : 'Tambah Produk' }}</h1>
      <router-link to="/penjual/produk" class="back-link">Kembali ke Daftar Produk</router-link>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <form v-if="!loading" class="modal-card toko-form" @submit.prevent="submit">
      <div class="form-group">
        <label>Nama Produk</label>
        <input v-model="form.nama_produk" type="text" required />
      </div>
      <div class="form-group">
        <label>Kategori</label>
        <select v-model="form.kategori_id" required>
          <option value="" disabled>-- Pilih Kategori --</option>
          <option v-for="k in kategori" :key="k.id" :value="String(k.id)">{{ k.nama_kategori }}</option>
        </select>
      </div>
      <div class="form-row-2">
        <div class="form-group">
          <label>Harga (Rp)</label>
          <input v-model="form.harga" type="number" min="1" required />
        </div>
        <div class="form-group">
          <label>Stok</label>
          <input v-model="form.stok" type="number" min="0" required />
        </div>
      </div>
      <div class="form-group">
        <label>Deskripsi (opsional)</label>
        <textarea v-model="form.deskripsi" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label>{{ isEdit ? 'Ganti Foto (opsional)' : 'Foto Produk' }} (JPG/PNG, maks 5 MB)</label>
        <input type="file" accept=".jpg,.jpeg,.png" @change="onFileChange" :required="!isEdit" />
        <img v-if="fotoUrl && !file" :src="fotoUrl" class="table-thumb" alt="" />
      </div>
      <div class="form-group">
        <label>Status</label>
        <select v-model="form.status">
          <option value="aktif">Aktif</option>
          <option value="nonaktif">Nonaktif</option>
        </select>
      </div>
      <div class="form-actions">
        <button class="btn-submit" type="submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : 'Simpan' }}
        </button>
      </div>
    </form>
  </div>
</template>
