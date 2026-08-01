<template>
  <div class="verify-container">
    <div class="verify-card">
      <!-- Header -->
      <div class="verify-header">
        <div class="logo-section">
          <div class="logo-placeholder">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h1>Verifikasi Anggota</h1>
          <p>Pramuka Jawa Barat</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="content-section loading-section">
        <div class="spinner"></div>
        <p>Memverifikasi anggota...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="content-section error-section">
        <div class="error-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="15" y1="9" x2="9" y2="15" />
            <line x1="9" y1="9" x2="15" y2="15" />
          </svg>
        </div>
        <h2>Verifikasi Gagal</h2>
        <p class="error-message">{{ error }}</p>
        <button @click="verifyMember" class="btn-retry">Coba Lagi</button>
      </div>

      <!-- Success State - Member Info -->
      <div v-else-if="memberData" class="content-section success-section">
        <div class="success-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        </div>

        <h2>Anggota Terverifikasi</h2>
        <p class="verify-subtitle">Data anggota di bawah ini telah terverifikasi</p>

        <!-- Member Information -->
        <div class="member-info">
          <div class="info-row">
            <span class="info-label">Nama Lengkap</span>
            <span class="info-value">{{ memberData.nama_lengkap }}</span>
          </div>

          <div class="info-row">
            <span class="info-label">Nomor Anggota</span>
            <span class="info-value">{{ memberData.nomor_anggota || '-' }}</span>
          </div>

          <div class="info-row">
            <span class="info-label">Golongan</span>
            <span class="info-value">{{ memberData.golongan || '-' }}</span>
          </div>

          <div class="info-row">
            <span class="info-label">Kwartir</span>
            <span class="info-value">{{ memberData.kwartir || '-' }}</span>
          </div>

          <div class="info-row">
            <span class="info-label">Status Keanggotaan</span>
            <span class="info-value">
              <span :class="['status-badge', `status-${memberData.membership_status}`]">
                {{ getStatusLabel(memberData.membership_status) }}
              </span>
            </span>
          </div>
        </div>

        <!-- Verification Badge -->
        <div class="verification-badge">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
            />
            <path d="M9 12l2 2 4-4" />
          </svg>
          <span>Terverifikasi Resmi</span>
        </div>

        <!-- Disclaimer -->
        <div class="disclaimer">
          <p>
            <strong>Catatan:</strong> Data ini bersifat publik dan hanya menampilkan
            informasi dasar keanggotaan untuk keperluan verifikasi.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <div class="verify-footer">
        <p>&copy; 2025 Pramuka Jawa Barat. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()

const loading = ref(true)
const error = ref(null)
const memberData = ref(null)

const verifyMember = async () => {
  loading.value = true
  error.value = null
  memberData.value = null

  const token = route.params.token

  if (!token) {
    error.value = 'Token verifikasi tidak ditemukan'
    loading.value = false
    return
  }

  try {
    // Use direct axios call without auth token for public endpoint
    const response = await axios.get(
      `http://localhost:8000/api/member/verify/${token}`
    )
    memberData.value = response.data
  } catch (err) {
    console.error('Error verifying member:', err)
    if (err.response?.status === 404) {
      error.value = 'Token verifikasi tidak valid atau anggota tidak ditemukan'
    } else if (err.response?.status === 400) {
      error.value = 'Format token tidak valid'
    } else {
      error.value = err.response?.data?.detail || 'Gagal memverifikasi anggota'
    }
  } finally {
    loading.value = false
  }
}

const getStatusLabel = (status) => {
  const labels = {
    active: 'Aktif',
    inactive: 'Tidak Aktif',
    expired: 'Kadaluarsa',
    pending: 'Menunggu'
  }
  return labels[status] || status
}

onMounted(() => {
  verifyMember()
})
</script>

<style scoped>
.verify-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.verify-card {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 100%;
  overflow: hidden;
}

.verify-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.logo-placeholder {
  width: 64px;
  height: 64px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.verify-header h1 {
  font-size: 1.75rem;
  font-weight: bold;
  margin: 0;
}

.verify-header p {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.content-section {
  padding: 3rem 2rem;
}

.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #7f8c8d;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}

.error-icon {
  color: #e74c3c;
}

.error-section h2 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin: 0;
}

.error-message {
  color: #e74c3c;
  font-size: 1rem;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: background-color 0.3s;
}

.btn-retry:hover {
  background-color: #5568d3;
}

.success-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.success-icon {
  color: #27ae60;
}

.success-section h2 {
  color: #2c3e50;
  font-size: 1.75rem;
  margin: 0;
}

.verify-subtitle {
  color: #7f8c8d;
  font-size: 1rem;
  margin: 0;
  text-align: center;
}

.member-info {
  width: 100%;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  color: #7f8c8d;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
  text-align: right;
}

.status-badge {
  display: inline-block;
  padding: 0.375rem 0.875rem;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-active {
  background-color: #d4edda;
  color: #155724;
}

.status-inactive {
  background-color: #e2e3e5;
  color: #383d41;
}

.status-expired {
  background-color: #f8d7da;
  color: #721c24;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.verification-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #d4edda;
  color: #155724;
  border-radius: 8px;
  font-weight: 600;
}

.disclaimer {
  width: 100%;
  padding: 1rem;
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
  font-size: 0.875rem;
  color: #856404;
}

.disclaimer strong {
  font-weight: 700;
}

.verify-footer {
  background-color: #f8f9fa;
  padding: 1.5rem;
  text-align: center;
  color: #7f8c8d;
  font-size: 0.875rem;
  border-top: 1px solid #e9ecef;
}

.verify-footer p {
  margin: 0;
}

@media (max-width: 640px) {
  .verify-container {
    padding: 1rem;
  }

  .content-section {
    padding: 2rem 1.5rem;
  }

  .info-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .info-value {
    text-align: left;
  }
}
</style>
