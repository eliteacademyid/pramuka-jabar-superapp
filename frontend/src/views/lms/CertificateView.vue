<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../../services/api'

const route = useRoute()
const router = useRouter()
const enrollmentId = route.params.id

const certData = ref(null)
const loading = ref(true)

async function fetchCertificate() {
  try {
    const res = await api.get(`/lms/enrollments/${enrollmentId}/certificate`)
    certData.value = res.data
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal memuat sertifikat')
    router.push('/admin/enrollments')
  } finally {
    loading.value = false
  }
}

function printCertificate() {
  window.print()
}

onMounted(() => {
  fetchCertificate()
})
</script>

<template>
  <div class="cert-page">
    <div class="cert-actions no-print">
      <router-link to="/admin/enrollments" class="btn-secondary">&larr; Kembali</router-link>
      <button class="btn-primary" @click="printCertificate" v-if="certData">Cetak / Download PDF</button>
    </div>

    <div v-if="loading" style="text-align: center; margin-top: 3rem;">
      Memuat data sertifikat...
    </div>

    <div v-else-if="certData" class="cert-container">
      <div class="cert-border">
        <div class="cert-content">
          <div class="cert-header">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Lambang_Pramuka.svg/1200px-Lambang_Pramuka.svg.png" alt="Logo Pramuka" class="cert-logo" />
            <h1>SERTIFIKAT KELULUSAN</h1>
            <p class="cert-subtitle">Kwartir Cabang Gerakan Pramuka Kabupaten Bandung Barat</p>
          </div>

          <div class="cert-body">
            <p>Diberikan kepada:</p>
            <h2 class="participant-name">{{ certData.issued_to }}</h2>
            <p>Atas kelulusannya dalam menyelesaikan program e-Pelatihan:</p>
            <h3 class="training-title">"{{ certData.training_title }}"</h3>
          </div>

          <div class="cert-footer">
            <div class="cert-meta">
              <p><strong>Nomor Sertifikat:</strong> {{ certData.certificate_id }}</p>
              <p><strong>Tanggal Diterbitkan:</strong> {{ certData.issue_date }}</p>
            </div>
            <div class="cert-signature">
              <div class="signature-line"></div>
              <p>Ketua Kwarcab KBB</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cert-page {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.cert-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.cert-container {
  background: white;
  padding: 1.5rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border-radius: 4px;
}

.cert-border {
  border: 12px double var(--brown);
  padding: 1rem;
  background: #fffdfa;
}

.cert-content {
  border: 2px solid var(--primary);
  padding: 3rem 4rem;
  text-align: center;
  position: relative;
}

.cert-header h1 {
  font-family: 'Times New Roman', serif;
  color: var(--brown);
  font-size: 2.8rem;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  letter-spacing: 2px;
}

.cert-subtitle {
  font-size: 1.2rem;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.cert-logo {
  height: 80px;
  opacity: 0.9;
}

.cert-body {
  margin: 3rem 0;
}

.participant-name {
  font-family: 'Georgia', serif;
  font-size: 2.5rem;
  color: #111;
  margin: 1rem 0;
  border-bottom: 1px solid #ccc;
  display: inline-block;
  padding: 0 2rem 0.5rem;
}

.training-title {
  font-size: 1.6rem;
  color: var(--brown);
  margin-top: 1rem;
}

.cert-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 4rem;
  text-align: left;
}

.cert-meta p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
  color: #666;
}

.cert-signature {
  text-align: center;
}

.signature-line {
  width: 200px;
  border-bottom: 1px solid #333;
  margin-bottom: 0.5rem;
  height: 40px;
}

/* Print Specific Styles */
@media print {
  @page {
    size: A4 landscape;
    margin: 0;
  }
  body * {
    visibility: hidden;
  }
  .cert-container, .cert-container * {
    visibility: visible;
  }
  .cert-container {
    position: absolute;
    left: 0;
    top: 0;
    width: 100vw;
    height: 100vh;
    box-shadow: none;
    padding: 0;
  }
  .cert-border {
    height: 96vh;
    box-sizing: border-box;
    margin: 2vh;
  }
  .cert-content {
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .no-print {
    display: none !important;
  }
}
</style>
