import api from './api'

// ─── Surat Masuk ────────────────────────────────────────────────────────────

export const getSuratMasuk = (params = {}) =>
  api.get('/surat-masuk', { params })

export const getSuratMasukDetail = (id) =>
  api.get(`/surat-masuk/${id}`)

export const createSuratMasuk = (data) =>
  api.post('/surat-masuk', data)

export const updateSuratMasuk = (id, data) =>
  api.put(`/surat-masuk/${id}`, data)

export const deleteSuratMasuk = (id) =>
  api.delete(`/surat-masuk/${id}`)

// ─── Surat Keluar ───────────────────────────────────────────────────────────

export const getSuratKeluar = (params = {}) =>
  api.get('/surat-keluar', { params })

export const getSuratKeluarDetail = (id) =>
  api.get(`/surat-keluar/${id}`)

export const createSuratKeluar = (data) =>
  api.post('/surat-keluar', data)

export const updateSuratKeluar = (id, data) =>
  api.put(`/surat-keluar/${id}`, data)

export const approveSuratKeluar = (id) =>
  api.post(`/surat-keluar/${id}/approve`)

export const deleteSuratKeluar = (id) =>
  api.delete(`/surat-keluar/${id}`)

// ─── Disposisi ──────────────────────────────────────────────────────────────

export const getDisposisi = (params = {}) =>
  api.get('/disposisi', { params })

export const createDisposisi = (data) =>
  api.post('/disposisi', data)

export const updateDisposisi = (id, data) =>
  api.put(`/disposisi/${id}`, data)

// ─── Lampiran ───────────────────────────────────────────────────────────────

export const uploadLampiran = (suratId, file) => {
  const formData = new FormData()
  formData.append('surat_id', suratId)
  formData.append('file', file)
  return api.post('/lampiran', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const downloadLampiranUrl = (id) =>
  `${api.defaults.baseURL}/lampiran/${id}/download`

export const deleteLampiran = (id) =>
  api.delete(`/lampiran/${id}`)

// ─── Tracking ───────────────────────────────────────────────────────────────

export const getTracking = (suratId) =>
  api.get(`/tracking/${suratId}`)
