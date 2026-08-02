// Task 2.4: Pelaksanaan API Service
import api from './api';

// Get list of pelaksanaan
export async function getPelaksanaan(params = {}) {
  return api.get('/pelaksanaan', { params });
}

// Get a single pelaksanaan by ID
export async function getPelaksanaanById(id) {
  return api.get(`/pelaksanaan/${id}`);
}

// Create a new pelaksanaan
export async function createPelaksanaan(payload) {
  return api.post('/pelaksanaan', payload);
}

// Update an existing pelaksanaan
export async function updatePelaksanaan(id, payload) {
  return api.put(`/pelaksanaan/${id}`, payload);
}

// Delete a pelaksanaan
export async function deletePelaksanaan(id) {
  return api.delete(`/pelaksanaan/${id}`);
}
