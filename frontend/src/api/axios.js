import axios from 'axios'
import { useAuthStore } from '../store/auth'
import { isTokenValid, clearAuthStorage } from '../utils/auth'

// Create Axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api',
  timeout: 15000,
  withCredentials: true,
})

// Request interceptor – attach JWT token from the auth store (or fallback to localStorage)
api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  // Prefer the token from the Pinia store; fall back to localStorage for safety
  const token = authStore.token || localStorage.getItem('token')
  if (token && isTokenValid(token)) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  } else if (token) {
    // Token exists but is expired/invalid – clean up and force logout
    clearAuthStorage()
    authStore.logout()
    window.location.href = '/login'
  }
  return config
})

// Response interceptor – handle authentication failures globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized – clear auth data and redirect to login page
      clearAuthStorage()
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default api
