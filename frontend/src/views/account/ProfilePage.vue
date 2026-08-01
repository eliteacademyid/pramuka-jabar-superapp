<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Profil & Alamat</h2>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div class="form-group" style="max-width: 400px">
      <label>Nama Lengkap</label>
      <input v-model="profile.nama_lengkap" />
      <label>Email</label>
      <input v-model="profile.email" />
      <button class="btn-submit" style="max-width: 200px" @click="saveProfile">Simpan Profil</button>
    </div>

    <h3>Alamat Pengiriman</h3>
    <div class="card-grid">
      <div v-for="a in addresses" :key="a.id" class="stat-card">
        <div class="stat-label"><strong>{{ a.label }}</strong> {{ a.is_primary ? '(utama)' : '' }}</div>
        <p>{{ a.address_line }}, {{ a.city }}, {{ a.province }}</p>
        <button class="btn-small btn-danger" @click="removeAddress(a)">Hapus</button>
      </div>
    </div>

    <h3>Tambah Alamat</h3>
    <div class="form-group" style="max-width: 400px">
      <label>Label</label>
      <input v-model="form.label" />
      <label>Alamat Lengkap</label>
      <input v-model="form.address_line" />
      <label>Kota</label>
      <input v-model="form.city" />
      <label>Provinsi</label>
      <input v-model="form.province" />
      <label class="checkbox-group">
        <input v-model="form.is_primary" type="checkbox" /> Jadikan alamat utama
      </label>
      <button class="btn-submit" style="max-width: 200px" @click="addAddress">Simpan Alamat</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'

const me = ref(null)
const profile = ref({ nama_lengkap: '', email: '' })
const addresses = ref([])
const form = ref({ label: 'rumah', address_line: '', city: '', province: '', is_primary: false })
const error = ref('')

async function load() {
  const [m, a] = await Promise.all([api.get('/auth/me'), api.get('/me/addresses')])
  me.value = m.data
  profile.value = { nama_lengkap: m.data.user.nama_lengkap, email: m.data.user.email || '' }
  addresses.value = a.data
}

async function saveProfile() {
  try {
    await api.put('/me', profile.value)
    alert('Profil disimpan')
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function addAddress() {
  try {
    await api.post('/me/addresses', form.value)
    form.value = { label: 'rumah', address_line: '', city: '', province: '', is_primary: false }
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function removeAddress(a) {
  await api.delete(`/me/addresses/${a.id}`)
  await load()
}

onMounted(load)
</script>
