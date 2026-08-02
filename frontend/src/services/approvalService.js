// Task 2.7: Approval API Service
import api from './api';

// Create an approval (admin only)
export async function createApproval(payload) {
  return api.post('/approval', payload);
}
