// Task 2.5: Realisasi API Service
import api from './api';

// Get list of realisasi with optional query parameters (pagination, search, status)
export async function getRealisasi(params = {}) {
  return api.get('/realisasi', { params });
}

// Create a new realisasi entry
export async function createRealisasi(payload) {
  return api.post('/realisasi', payload);
}
