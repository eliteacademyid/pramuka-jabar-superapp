// Task 2.1: Authentication API Service
import api from './api';

export async function login(payload) {
  return api.post('/auth/login', payload);
}

export async function getProfile() {
  return api.get('/auth/me');
}
