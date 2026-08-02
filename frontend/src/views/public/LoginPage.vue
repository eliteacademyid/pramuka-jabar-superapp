<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

async function handleSubmit() {
  errorMessage.value = ''
  loading.value = true
  try {
    const res = await api.post('/auth/login', {
      username: username.value,
      password: password.value
    })
    localStorage.setItem('token', res.data.access_token)
    const me = await api.get('/auth/me')
    localStorage.setItem('role', me.data.role)
    if (me.data.role === 'kontributor') router.push({ name: 'kontributor-dashboard' })
    else if (me.data.role === 'penjual') router.push({ name: 'penjual-dashboard' })
    else router.push({ name: 'admin-dashboard' })
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail || 'Terjadi kesalahan. Coba lagi.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="handleSubmit">
      <div class="logo-circle small"></div>
      <h2>Masuk Admin</h2>
      <p class="subtitle">Super Apps Pramuka Jawa Barat</p>

      <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

      <div class="form-group">
        <label for="username">Username</label>
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          placeholder="Masukkan username"
          required
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="Masukkan password"
          required
        />
      </div>

      <button class="btn-submit" type="submit" :disabled="loading">
        {{ loading ? 'Memproses...' : 'Masuk' }}
      </button>

      <router-link to="/" class="back-link">Kembali ke beranda</router-link>
    </form>
  </div>
</template>
