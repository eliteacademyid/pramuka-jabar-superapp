<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
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
    const { fetchMe, homeForRole } = await import('../../services/session')
    const me = await fetchMe(true)
    const redirect = route.query.redirect
    router.push(redirect ? String(redirect) : homeForRole(me))
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
      <h2>Masuk</h2>
      <p class="subtitle">SuperApps Pramuka Jawa Barat</p>
      <p class="subtitle kw">Kwartir Daerah Jawa Barat — terbuka untuk semua</p>

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
