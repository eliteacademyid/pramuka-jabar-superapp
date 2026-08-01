import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
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
    localStorage.setItem('user', JSON.stringify(response.data))
    return response
  }

  async function initialize() {
    if (!token.value) {
      return false
    }

    try {
      await getProfile()
      return true
    } catch (error) {
      logout()
      return false
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAuthenticated, login, logout, getProfile, initialize }
})
