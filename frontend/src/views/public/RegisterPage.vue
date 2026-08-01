<template>
  <div class="login-page">
    <div class="login-card">
      <h2>Daftar LomaScout</h2>
      <p class="subtitle">Bergabung untuk belanja & membuka toko</p>

      <div v-if="error" class="alert-error">{{ error }}</div>

      <form @submit.prevent="submit">
        <div class="form-group">
          <label>Nama Lengkap</label>
          <input v-model="form.nama_lengkap" required />
        </div>
        <div class="form-group">
          <label>Username</label>
          <input v-model="form.username" minlength="3" required />
        </div>
        <div class="form-group">
          <label>Password (min 8 karakter)</label>
          <input v-model="form.password" type="password" minlength="8" required />
        </div>
        <div class="form-group">
          <label>Tipe Akun</label>
          <select v-model="form.account_type">
            <option value="anggota">Anggota Pramuka</option>
            <option value="umum">Masyarakat Umum</option>
          </select>
        </div>
        <template v-if="form.account_type === 'anggota'">
          <div class="form-group">
            <label>Nomor Anggota (sintetis)</label>
            <input v-model="form.scout_number" placeholder="SK-000-000" />
          </div>
          <div class="form-group">
            <label>Kwartir</label>
            <input v-model="form.kwartir" />
          </div>
          <div class="form-group">
            <label>Golongan</label>
            <select v-model="form.golongan">
              <option value="Siaga">Siaga</option>
              <option value="Penggalang">Penggalang</option>
              <option value="Penegak">Penegak</option>
              <option value="Pandega">Pandega</option>
              <option value="Pembina">Pembina</option>
            </select>
          </div>
        </template>

        <button class="btn-submit" :disabled="loading" type="submit">
          {{ loading ? 'Mendaftar…' : 'Daftar' }}
        </button>
      </form>

      <router-link class="back-link" to="/login">Sudah punya akun? Masuk</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { getErrorMessage } from '../../services/api'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const form = ref({
  nama_lengkap: '',
  username: '',
  password: '',
  account_type: 'anggota',
  scout_number: '',
  kwartir: '',
  golongan: 'Penggalang'
})

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await api.post('/auth/register', form.value)
    router.push({ name: 'login', query: { registered: '1' } })
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>
