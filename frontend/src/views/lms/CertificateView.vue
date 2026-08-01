<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

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
  const element = document.querySelector('.cert-container');
  const opt = {
    margin:       0,
    filename:     `Sertifikat-${certData.value.issued_to.replace(/\s+/g, '_')}.pdf`,
    image:        { type: 'jpeg', quality: 0.98 },
    html2canvas:  { scale: 2, useCORS: true },
    jsPDF:        { unit: 'in', format: 'a4', orientation: 'landscape' }
  };
  
  // Use html2pdf if available globally (from CDN)
  if (window.html2pdf) {
    window.html2pdf().set(opt).from(element).save();
  } else {
    // Fallback to print if CDN failed to load
    window.print();
  }
}

onMounted(() => {
  fetchCertificate()
})
</script>

<template>
  <div class="max-w-5xl mx-auto p-4 sm:p-8 min-h-screen flex flex-col justify-center">
    <div class="flex flex-col sm:flex-row justify-between items-center mb-8 no-print gap-4">
      <router-link to="/admin/enrollments" class="btn-secondary">&larr; Kembali</router-link>
      <button class="btn-primary shadow-lg hover:shadow-xl transition-all" @click="printCertificate" v-if="certData">
        Cetak / Download PDF
      </button>
    </div>

    <div v-if="loading" class="text-center mt-12 text-gray-500 animate-pulse font-medium text-lg">
      Memuat data sertifikat...
    </div>

    <div v-else-if="certData" class="cert-container w-full bg-white shadow-2xl rounded-2xl overflow-hidden relative">
      <!-- Decorative Modern Elements -->
      <div class="absolute top-0 left-0 w-full h-3 bg-gradient-to-r from-[var(--brown)] via-[var(--gold)] to-[var(--maroon)]"></div>
      <div class="absolute -top-32 -right-32 w-64 h-64 bg-[var(--gold)] opacity-10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-32 -left-32 w-64 h-64 bg-[var(--maroon)] opacity-10 rounded-full blur-3xl"></div>

      <div class="cert-border m-2 sm:m-4 md:m-8 border-[6px] md:border-[12px] border-double border-[var(--brown)] p-2 md:p-4 bg-[#fffdfa] rounded-xl relative z-10">
        <div class="cert-content border-2 border-[var(--gold)] p-6 sm:p-12 md:p-16 text-center flex flex-col justify-center rounded-lg min-h-[500px]">
          
          <div class="cert-header flex flex-col items-center">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Lambang_Pramuka.svg/1200px-Lambang_Pramuka.svg.png" alt="Logo Pramuka" class="h-16 md:h-24 opacity-90 drop-shadow-md mb-4" />
            <h1 class="font-serif text-[var(--brown)] text-3xl sm:text-4xl md:text-5xl lg:text-6xl tracking-widest font-bold mb-2">
              SERTIFIKAT KELULUSAN
            </h1>
            <p class="text-sm sm:text-base md:text-lg text-gray-600 uppercase tracking-widest font-medium">
              Kwartir Cabang Gerakan Pramuka Kabupaten Bandung Barat
            </p>
          </div>

          <div class="cert-body my-8 sm:my-12">
            <p class="text-gray-500 italic mb-2 sm:mb-4">Diberikan dengan bangga kepada:</p>
            <h2 class="font-serif text-3xl sm:text-4xl md:text-5xl text-gray-900 border-b-2 border-gray-300 inline-block px-4 sm:px-8 pb-2 sm:pb-4 mb-4 sm:mb-6 font-semibold text-transparent bg-clip-text bg-gradient-to-r from-gray-900 to-gray-600">
              {{ certData.issued_to }}
            </h2>
            <p class="text-gray-500 italic mb-2 sm:mb-4 max-w-2xl mx-auto">
              Atas dedikasi dan kelulusannya dalam menyelesaikan program e-Pelatihan:
            </p>
            <h3 class="text-xl sm:text-2xl md:text-3xl text-[var(--maroon)] font-bold px-4">
              "{{ certData.training_title }}"
            </h3>
          </div>

          <div class="cert-footer mt-auto flex flex-col sm:flex-row justify-between items-center sm:items-end text-left gap-8 sm:gap-0">
            <div class="cert-meta text-center sm:text-left text-sm md:text-base text-gray-600 space-y-1">
              <p><strong class="text-gray-800">Nomor Sertifikat:</strong> <br class="sm:hidden"/> {{ certData.certificate_id }}</p>
              <p><strong class="text-gray-800">Tanggal Diterbitkan:</strong> <br class="sm:hidden"/> {{ certData.issue_date }}</p>
            </div>
            <div class="cert-signature text-center flex flex-col items-center">
              <div class="w-40 sm:w-48 h-12 md:h-16 border-b border-gray-800 mb-2 relative">
                 <!-- Dummy Signature for aesthetics -->
                 <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Signature_of_Robert_Baden-Powell.svg" class="absolute bottom-1 w-24 left-1/2 -translate-x-1/2 opacity-60" alt="TTD">
              </div>
              <p class="font-semibold text-gray-800">Ketua Kwarcab KBB</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
    box-shadow: none !important;
    border-radius: 0 !important;
    padding: 0;
    margin: 0;
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
