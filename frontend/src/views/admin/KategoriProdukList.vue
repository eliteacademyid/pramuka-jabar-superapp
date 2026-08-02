<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const kategori = ref([])
const loading = ref(true)
const errorMessage = ref('')
const saving = ref(false)

const showForm = ref(false)
const editId = ref(null)
const namaKategori = ref('')

async function muat() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/marketplace/kategori-produk')
    kategori.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat kategori.'
  } finally {
    loading.value = false
  }
}

onMounted(muat)

function mulaiTambah() {
  editId.value = null
  namaKategori.value = ''
  showForm.value = true
}

function mulaiEdit(k) {
  editId.value = k.id
  namaKategori.value = k.nama_kategori
  showForm.value = true
}

async function submit() {
  errorMessage.value = ''
  if (!namaKategori.value.trim()) {
    errorMessage.value = 'Nama kategori wajib diisi.'
    return
  }
  saving.value = true
  try {
    if (editId.value) {
      await api.put(`/admin/marketplace/kategori-produk/${editId.value}`, {
        nama_kategori: namaKategori.value.trim()
      })
    } else {
      await api.post('/admin/marketplace/kategori-produk', {
        nama_kategori: namaKategori.value.trim()
      })
    }
    showForm.value = false
    await muat()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan kategori.'
  } finally {
    saving.value = false
  }
}

async function hapus(k) {
  if (!confirm(`Hapus kategori "${k.nama_kategori}"?`)) return
  try {
    await api.delete(`/admin/marketplace/kategori-produk/${k.id}`)
    await muat()
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menghapus kategori.'
  }
}
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>Kategori Produk</h1>
      <button class="btn-primary" @click="mulaiTambah">+ Tambah Kategori</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="loading" class="greeting">Memuat kategori...</div>

    <table v-else-if="kategori.length" class="data-table">
      <thead>
        <tr>
          <th>Nama Kategori</th>
          <th>Dibuat</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="k in kategori" :key="k.id">
          <td>{{ k.nama_kategori }}</td>
          <td>{{ new Date(k.created_at).toLocaleDateString('id-ID') }}</td>
          <td>
            <div class="row-actions">
              <button class="btn-small" @click="mulaiEdit(k)">Edit</button>
              <button class="btn-small btn-danger" @click="hapus(k)">Hapus</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-row">Belum ada kategori.</div>

    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <form class="modal-card" @submit.prevent="submit">
        <div class="modal-actions">
          <h2>{{ editId ? 'Edit Kategori' : 'Tambah Kategori' }}</h2>
          <button type="button" class="btn-cancel" @click="showForm = false">Tutup</button>
        </div>
        <div class="form-group">
          <label>Nama Kategori</label>
          <input v-model="namaKategori" type="text" required />
        </div>
        <div class="form-actions">
          <button class="btn-submit" type="submit" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
