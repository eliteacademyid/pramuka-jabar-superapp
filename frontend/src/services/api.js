import axios from 'axios'

const host = window.location.hostname
const apiBase =
  import.meta.env.VITE_API_URL ||
  `http://${host === 'localhost' || host === '127.0.0.1' ? 'localhost' : host}:8000/api`

const api = axios.create({
  baseURL: apiBase
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export function getErrorMessage(err) {
  if (err.response && err.response.data && err.response.data.detail) {
    const detail = err.response.data.detail
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg).join('; ')
    }
    return detail
  }
  return err.message || 'Terjadi kesalahan'
}

export default api
