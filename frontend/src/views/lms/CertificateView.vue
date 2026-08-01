<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import ActionModal from '../../components/ActionModal.vue'

const route = useRoute()
const router = useRouter()
const enrollmentId = route.params.id

const certData = ref(null)
const loading = ref(true)
const downloading = ref(false)
const modal = ref({ show: false, type: 'success', title: '', message: '' })

function showModal(type, title, message) {
  modal.value = { show: true, type, title, message }
}

async function fetchCertificate() {
  try {
    const res = await api.get(`/lms/enrollments/${enrollmentId}/certificate`)
    certData.value = res.data
  } catch (err) {
    showModal('error', 'Gagal Memuat', err.response?.data?.detail || 'Sertifikat tidak dapat dimuat.')
    setTimeout(() => router.push('/admin/enrollments'), 2500)
  } finally {
    loading.value = false
  }
}

async function downloadPDF() {
  if (!certData.value) return
  downloading.value = true
  try {
    const { default: html2pdf } = await import('html2pdf.js')
    const element = document.querySelector('.cert-container')
    const opt = {
      margin: 0,
      filename: `Sertifikat-${certData.value.issued_to.replace(/\s+/g, '_')}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, logging: false },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'landscape' }
    }
    await html2pdf().set(opt).from(element).save()
    showModal('success', 'Berhasil Diunduh', `Sertifikat atas nama ${certData.value.issued_to} berhasil diunduh sebagai PDF.`)
  } catch (err) {
    showModal('error', 'Gagal Download', 'Terjadi kesalahan saat membuat PDF. Silakan coba lagi.')
  } finally {
    downloading.value = false
  }
}

onMounted(() => { fetchCertificate() })
</script>

<template>
  <div class="cert-page">
    <ActionModal
      :show="modal.show"
      :type="modal.type"
      :title="modal.title"
      :message="modal.message"
      @close="modal.show = false"
    />

    <!-- Controls -->
    <div class="cert-controls no-print">
      <router-link to="/admin/enrollments" class="back-btn">&larr; Kembali</router-link>
      <button v-if="certData" class="download-btn" @click="downloadPDF" :disabled="downloading">
        <svg v-if="!downloading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <span class="btn-spinner" v-else></span>
        {{ downloading ? 'Menyiapkan PDF...' : 'Download PDF' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="cert-loading">
      <div class="spinner"></div>
      <p>Memuat sertifikat...</p>
    </div>

    <!-- Certificate -->
    <div v-else-if="certData" class="cert-container">
      <!-- Top bar accent -->
      <div class="cert-topbar"></div>

      <!-- Outer border -->
      <div class="cert-outer">
        <div class="cert-inner">

          <!-- Header -->
          <div class="cert-header">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Lambang_Pramuka.svg/1200px-Lambang_Pramuka.svg.png"
                 alt="Logo Pramuka" class="cert-logo" />
            <h1 class="cert-main-title">SERTIFIKAT KELULUSAN</h1>
            <p class="cert-org">Kwartir Cabang Gerakan Pramuka Kabupaten Bandung Barat</p>
            <div class="cert-divider"></div>
          </div>

          <!-- Body -->
          <div class="cert-body">
            <p class="cert-subtitle">Diberikan dengan bangga kepada:</p>
            <h2 class="cert-name">{{ certData.issued_to }}</h2>
            <p class="cert-subtitle">Atas dedikasi dan kelulusannya dalam menyelesaikan program e-Pelatihan:</p>
            <h3 class="cert-training">"{{ certData.training_title }}"</h3>
          </div>

          <!-- Footer -->
          <div class="cert-footer">
            <div class="cert-meta">
              <p><span class="meta-label">Nomor Sertifikat</span><br><strong>{{ certData.certificate_id }}</strong></p>
              <p><span class="meta-label">Tanggal Diterbitkan</span><br><strong>{{ certData.issue_date }}</strong></p>
            </div>
            <div class="cert-sign">
              <div class="sign-line"></div>
              <p class="sign-name">Ketua Kwarcab KBB</p>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cert-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

/* Controls */
.cert-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
  flex-wrap: wrap;
}
.back-btn {
  display: inline-flex; align-items: center;
  color: var(--brown); font-weight: 600; font-size: 0.9rem;
  text-decoration: none; background: white;
  padding: 0.5rem 1rem; border-radius: 10px;
  border: 1px solid #f0ebe4; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: all 0.2s;
}
.back-btn:hover { color: var(--maroon); background: #faf6f0; }

.download-btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: linear-gradient(135deg, var(--maroon), var(--brown-dark));
  color: white; font-weight: 700; font-size: 0.95rem;
  padding: 0.65rem 1.5rem; border-radius: 10px; border: none;
  cursor: pointer; box-shadow: 0 4px 14px rgba(123,36,28,0.25);
  transition: all 0.2s;
}
.download-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(123,36,28,0.35); }
.download-btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }
.download-btn svg { width: 18px; height: 18px; }
.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid white; border-top-color: transparent;
  border-radius: 50%; animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

/* Loading */
.cert-loading {
  display: flex; flex-direction: column; align-items: center;
  gap: 1rem; padding: 5rem 2rem; color: #6b7280;
}
.spinner {
  width: 48px; height: 48px;
  border: 4px solid #e5e7eb; border-top-color: var(--gold);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}

/* Certificate */
.cert-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.12);
  overflow: hidden;
  position: relative;
}

.cert-topbar {
  height: 8px;
  background: linear-gradient(90deg, var(--brown), var(--gold), var(--maroon));
}

.cert-outer {
  border: 10px double var(--brown);
  margin: 1.5rem;
  border-radius: 12px;
  background: #fffef9;
}
.cert-inner {
  border: 2px solid var(--gold);
  margin: 0.5rem;
  border-radius: 8px;
  padding: 3rem 3.5rem;
  display: flex; flex-direction: column; gap: 1.5rem;
  min-height: 480px; justify-content: center;
}

.cert-header { text-align: center; }
.cert-logo { height: 80px; margin-bottom: 1rem; opacity: 0.9; }
.cert-main-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: clamp(1.6rem, 4vw, 3rem);
  color: var(--brown);
  letter-spacing: 0.12em;
  font-weight: 700; margin: 0 0 0.4rem;
}
.cert-org {
  font-size: 0.85rem; color: #6b7280;
  text-transform: uppercase; letter-spacing: 0.1em;
}
.cert-divider {
  width: 80px; height: 3px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  margin: 1rem auto 0;
  border-radius: 2px;
}

.cert-body { text-align: center; padding: 0.5rem 0; }
.cert-subtitle { font-style: italic; color: #9ca3af; font-size: 0.9rem; margin: 0 0 0.75rem; }
.cert-name {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  color: #111827; font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
  display: inline-block; padding-bottom: 0.5rem;
  margin: 0 0 1rem;
}
.cert-training {
  font-size: clamp(1rem, 2.5vw, 1.5rem);
  color: var(--maroon); font-weight: 700;
  margin: 0.5rem 0 0;
}

.cert-footer {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-top: 1rem;
  flex-wrap: wrap; gap: 1.5rem;
}
.cert-meta p { margin: 0 0 0.5rem; font-size: 0.85rem; color: #374151; }
.meta-label { color: #9ca3af; font-size: 0.75rem; display: block; margin-bottom: 0.1rem; }
.cert-sign { text-align: center; }
.sign-line { width: 160px; border-bottom: 1.5px solid #374151; margin-bottom: 0.4rem; }
.sign-name { font-weight: 600; color: #374151; font-size: 0.875rem; }

/* Print */
@media print {
  @page { size: A4 landscape; margin: 0; }
  .no-print { display: none !important; }
  .cert-page { padding: 0; max-width: 100%; }
  .cert-container { border-radius: 0; box-shadow: none; }
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .cert-inner { padding: 1.5rem 1rem; }
  .cert-outer { margin: 0.75rem; }
}
</style>
