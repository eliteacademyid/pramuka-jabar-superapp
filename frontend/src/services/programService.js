// Task 2.2: Program API Service
import api from './api';

// Get list of programs
export async function getPrograms(params = {}) {
  return api.get('/programs', { params });
}

// Get a single program by ID
export async function getProgram(id) {
  return api.get(`/programs/${id}`);
}

// Create a new program
export async function createProgram(payload) {
  return api.post('/programs', payload);
}

// Update an existing program
export async function updateProgram(id, payload) {
  return api.put(`/programs/${id}`, payload);
}

// Delete a program
export async function deleteProgram(id) {
  return api.delete(`/programs/${id}`);
}
