<template>
  <div class="page-container">
    <div class="page-header"><h2>Toko Saya</h2></div>

    <div v-if="error" class="alert-error">{{ error }}</div>
    <div v-if="notice" class="alert-success">{{ notice }}</div>

    <template v-if="store">
      <p><strong>{{ store.name }}</strong> — <span class="status" :class="'status-' + (store.status === 'active' ? 'active' : 'inactive')">{{ store.status }}</span></p>
      <p v-if="store.reject_reason" class="hint">Alasan penolakan: {{ store.reject_reason }}</p>
      <div v-if="store.status === 'pending'" class="hint">Menunggu persetujuan admin.</div>
      <template v-if="store.status === 'active'">
        <div class="form-group" style="max-width: 400px">
          <label>Deskripsi</label>
          <textarea v-model="form.description" rows="3"></textarea>
          <label>Telepon</label>
          <input v-model="form.phone" />
          <button class="btn-submit" style="max-width: 200px" @click="save">Simpan</button>
        </div>
      </template>
    </template>

    <template v-else>
      <h3>Buka Toko Baru</h3>
      <div class="form-group" style="max-width: 400px">
        <label>Nama Toko</label>
        <input v-model="create.name" required />
        <label>Kota</label>
        <input v-model="create.city" required />
        <label>Provinsi</label>
        <input v-model="create.province" required />
        <label>Deskripsi</label>
        <textarea v-model="create.description" rows="3"></textarea>
        <button class="btn-submit" style="max-width: 200px" @click="submit">Ajukan Toko</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'
import { fetchMe } from '../../services/session'

const store = ref(null)
const error = ref('')
const notice = ref('')
const form = ref({ description: '', phone: '' })
const create = ref({ name: '', city: '', province: '', description: '' })

async function load() {
  try {
    const { data } = await api.get('/seller/store')
    store.value = data
    form.value = { description: data.description || '', phone: data.phone || '' }
  } catch {
    store.value = null
  }
}

async function submit() {
  try {
    await api.post('/seller/store', create.value)
    notice.value = 'Toko diajukan, menunggu persetujuan admin.'
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function save() {
  try {
    await api.put('/seller/store', form.value)
    notice.value = 'Tersimpan'
    await fetchMe(true)
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

onMounted(load)
</script>
