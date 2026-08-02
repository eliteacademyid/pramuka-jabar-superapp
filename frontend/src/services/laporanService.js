// Task 2.6: Laporan API Service
import api from './api';

// Get list of laporan with optional query parameters (pagination, status)
export async function getLaporan(params = {}) {
  return api.get('/laporan', { params });
}

// Create a new laporan entry
export async function createLaporan(payload) {
  return api.post('/laporan', payload);
}
