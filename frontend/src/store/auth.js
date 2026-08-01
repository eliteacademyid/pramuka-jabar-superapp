import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(credentials) {
    const response = await api.post('/auth/login', credentials)
    token.value = response.data.access_token
    localStorage.setItem('token', token.value)
    await getProfile()
    return response
  }

  async function getProfile() {
    const response = await api.get('/auth/me')
    user.value = response.data
    return response
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isAuthenticated, login, logout, getProfile }
})
