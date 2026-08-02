// Task 2.3: Kegiatan API Service
import api from './api';

// Get list of kegiatan
export async function getKegiatans(params = {}) {
  return api.get('/kegiatans', { params });
}

// Get a single kegiatan by ID
export async function getKegiatan(id) {
  return api.get(`/kegiatans/${id}`);
}

// Create a new kegiatan
export async function createKegiatan(payload) {
  return api.post('/kegiatans', payload);
}

// Update an existing kegiatan
export async function updateKegiatan(id, payload) {
  return api.put(`/kegiatans/${id}`, payload);
}

// Delete a kegiatan
export async function deleteKegiatan(id) {
  return api.delete(`/kegiatans/${id}`);
}
