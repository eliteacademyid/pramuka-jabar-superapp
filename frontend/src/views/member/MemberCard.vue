<template>
  <div class="member-card-container">
    <div class="page-header">
      <h1>Kartu Anggota Digital</h1>
      <p>Kartu anggota Pramuka Jawa Barat</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <p>Memuat kartu anggota...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="fetchMemberCard" class="btn-retry">Coba Lagi</button>
    </div>

    <!-- Member Card Display -->
    <div v-else-if="memberCard" class="card-wrapper">
      <div class="digital-card">
        <!-- Card Header -->
        <div class="card-header">
          <h2>PRAMUKA JAWA BARAT</h2>
          <p class="card-subtitle">Kartu Anggota Digital</p>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <!-- Photo Section -->
          <div class="photo-section">
            <div class="photo-frame">
              <img
                v-if="memberCard.foto_url"
                :src="memberCard.foto_url"
                :alt="memberCard.nama_lengkap"
                class="member-photo"
              />
              <div v-else class="photo-placeholder">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Member Info Section -->
          <div class="info-section">
            <div class="info-item">
              <label>Nama Lengkap</label>
              <p class="info-value">{{ memberCard.nama_lengkap }}</p>
            </div>

            <div class="info-item">
              <label>Nomor Anggota</label>
              <p class="info-value">{{ memberCard.nomor_anggota || '-' }}</p>
            </div>

            <div class="info-item">
              <label>Golongan</label>
              <p class="info-value">{{ memberCard.golongan || '-' }}</p>
            </div>

            <div class="info-item">
              <label>Kwartir</label>
              <p class="info-value">{{ memberCard.kwartir || '-' }}</p>
            </div>

            <div class="info-item">
              <label>Status Keanggotaan</label>
              <p class="info-value">
                <span :class="['status-badge', `status-${memberCard.membership_status}`]">
                  {{ getStatusLabel(memberCard.membership_status) }}
                </span>
              </p>
            </div>

            <div class="info-item">
              <label>Masa Berlaku</label>
              <p class="info-value">{{ formatDate(memberCard.valid_until) }}</p>
            </div>
          </div>
        </div>

        <!-- QR Code Section -->
        <div class="card-footer">
          <div class="qr-section">
            <div v-if="qrCodeLoading" class="qr-loading">
              <p>Memuat QR Code...</p>
            </div>
            <div v-else-if="qrCodeData" class="qr-code-container">
              <canvas ref="qrCanvas" class="qr-code"></canvas>
              <p class="qr-instruction">Scan QR Code untuk verifikasi</p>
            </div>
            <div v-else-if="qrCodeError" class="qr-error">
              <p>{{ qrCodeError }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Verification Link -->
      <div v-if="qrCodeData" class="verification-link">
        <p>Link Verifikasi:</p>
        <a :href="qrCodeData.verification_url" target="_blank" class="link">
          {{ qrCodeData.verification_url }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import QRCode from 'qrcode'

const router = useRouter()

const loading = ref(true)
const error = ref(null)
const memberCard = ref(null)

const qrCodeLoading = ref(false)
const qrCodeData = ref(null)
const qrCodeError = ref(null)
const qrCanvas = ref(null)

const fetchMemberCard = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await api.get('/member/card')
    memberCard.value = response.data
    
    // Fetch QR code after card data is loaded
    await fetchQRCode()
  } catch (err) {
    console.error('Error fetching member card:', err)
    if (err.response?.status === 401) {
      error.value = 'Sesi Anda telah berakhir. Silakan login kembali.'
      setTimeout(() => {
        localStorage.removeItem('token')
        router.push('/login')
      }, 2000)
    } else {
      error.value = err.response?.data?.detail || 'Gagal memuat kartu anggota'
    }
  } finally {
    loading.value = false
  }
}

const fetchQRCode = async () => {
  qrCodeLoading.value = true
  qrCodeError.value = null

  try {
    const response = await api.get('/member/qrcode')
    qrCodeData.value = response.data
    
    // Generate QR Code on canvas
    await generateQRCode(response.data.qr_code_url)
  } catch (err) {
    console.error('Error fetching QR code:', err)
    qrCodeError.value = err.response?.data?.detail || 'Gagal memuat QR Code'
  } finally {
    qrCodeLoading.value = false
  }
}

const generateQRCode = async (url) => {
  if (!qrCanvas.value) return

  try {
    await QRCode.toCanvas(qrCanvas.value, url, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
  } catch (err) {
    console.error('Error generating QR code:', err)
    qrCodeError.value = 'Gagal membuat QR Code'
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

const formatDate = (date) => {
  if (!date) return '-'
  
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(date).toLocaleDateString('id-ID', options)
}

onMounted(() => {
  fetchMemberCard()
})
</script>

<style scoped>
.member-card-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #7f8c8d;
  font-size: 1rem;
}

.loading,
.error-message {
  text-align: center;
  padding: 3rem 1rem;
}

.error-message {
  color: #e74c3c;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-retry:hover {
  background-color: #2980b9;
}

.card-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.digital-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  color: white;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 1rem;
}

.card-header h2 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
  letter-spacing: 1px;
}

.card-subtitle {
  font-size: 0.9rem;
  opacity: 0.9;
}

.card-body {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.photo-section {
  display: flex;
  align-items: flex-start;
}

.photo-frame {
  width: 120px;
  height: 150px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.member-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.75rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 1rem;
  font-weight: 600;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-active {
  background-color: #27ae60;
  color: white;
}

.status-inactive {
  background-color: #95a5a6;
  color: white;
}

.status-expired {
  background-color: #e74c3c;
  color: white;
}

.status-pending {
  background-color: #f39c12;
  color: white;
}

.card-footer {
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 1.5rem;
}

.qr-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.qr-loading,
.qr-error {
  padding: 2rem;
  text-align: center;
}

.qr-error {
  color: #ffcdd2;
}

.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.qr-code {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
}

.qr-instruction {
  font-size: 0.875rem;
  opacity: 0.9;
  text-align: center;
}

.verification-link {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
}

.verification-link p {
  color: #7f8c8d;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.verification-link .link {
  color: #3498db;
  word-break: break-all;
  font-size: 0.875rem;
}

.verification-link .link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .card-body {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .photo-section {
    justify-content: center;
  }

  .digital-card {
    padding: 1.5rem;
  }
}
</style>
