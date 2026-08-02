import axios from 'axios'

const api = axios.create({
  baseURL: 'https://app2.team2.opencode.eliteacademy.id/api'
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
