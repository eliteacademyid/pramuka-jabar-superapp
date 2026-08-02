import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, getProfile as apiGetProfile } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(credentials) {
    const payload = {
      username: credentials.username,
      password: credentials.password
    }

    const response = await apiLogin(payload)
    const accessToken = response.data.access_token
    token.value = accessToken
    localStorage.setItem('token', accessToken)
    await apiGetProfile()
    return response
  }

  async function getProfile() {
    const response = await apiGetProfile()
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

  function clearSession() {
    logout()
  }

  return { token, user, isAuthenticated, login, logout, clearSession, getProfile, initialize }
})
