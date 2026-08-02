<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const stats = ref({ totalAnggota: 0, totalGudep: 0, totalWilayah: 0, totalCapaian: 0 })
const rekapJenjang = ref([])
const rekapWilayah = ref([])

onMounted(async () => {
  try {
    const [anggota, gudep, wilayah, capaian, byJenjang, byWilayah] = await Promise.all([
      api.get('/anggota/'),
      api.get('/gudep'),
      api.get('/wilayah'),
      api.get('/capaian-kompetensi/'),
      api.get('/rekap/anggota/jenjang'),
      api.get('/rekap/anggota/kota-kabupaten')
    ])
    stats.value.totalAnggota = anggota.data.length
    stats.value.totalGudep = gudep.data.length
    stats.value.totalWilayah = wilayah.data.length
    stats.value.totalCapaian = capaian.data.length
    rekapJenjang.value = byJenjang.data
    rekapWilayah.value = byWilayah.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
})

const jenjangLabels = { siaga: 'Siaga', penggalang: 'Penggalang', penegak: 'Penegak', pandega: 'Pandega', dewasa: 'Dewasa' }

function totalRekap(list) {
  return list.reduce((acc, item) => acc + (item.jumlah || 0), 0)
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Dashboard Keanggotaan</h2>
        <p class="greeting">Ringkasan data potensi keanggotaan Gerakan Pramuka.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="card-grid" v-if="!loading">
      <div class="stat-card">
        <span class="stat-value">{{ stats.totalAnggota }}</span>
        <span class="stat-label">Total Anggota</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.totalGudep }}</span>
        <span class="stat-label">Total Gudep</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.totalWilayah }}</span>
        <span class="stat-label">Total Wilayah</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.totalCapaian }}</span>
        <span class="stat-label">Total Capaian Kompetensi</span>
      </div>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div class="rekap-grid" v-if="!loading">
      <div class="rekap-card">
        <h3>Rekap Anggota per Jenjang</h3>
        <table class="data-table">
          <thead>
            <tr><th>Jenjang</th><th>Jumlah</th></tr>
          </thead>
          <tbody>
            <tr v-for="item in rekapJenjang" :key="item.jenjang">
              <td>{{ jenjangLabels[item.jenjang] || item.jenjang }}</td>
              <td>{{ item.jumlah }}</td>
            </tr>
            <tr v-if="rekapJenjang.length === 0">
              <td colspan="2" class="empty-row">Belum ada data anggota.</td>
            </tr>
            <tr v-if="rekapJenjang.length > 0">
              <td><strong>Total</strong></td>
              <td><strong>{{ totalRekap(rekapJenjang) }}</strong></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="rekap-card">
        <h3>Rekap Anggota per Kota/Kabupaten</h3>
        <table class="data-table">
          <thead>
            <tr><th>Kota/Kabupaten</th><th>Jumlah</th></tr>
          </thead>
          <tbody>
            <tr v-for="item in rekapWilayah" :key="item.kota_kabupaten">
              <td>{{ item.kota_kabupaten }}</td>
              <td>{{ item.jumlah }}</td>
            </tr>
            <tr v-if="rekapWilayah.length === 0">
              <td colspan="2" class="empty-row">Belum ada data anggota.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rekap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.25rem;
  margin-top: 1.5rem;
}

.rekap-card {
  background: var(--white);
  border: 2px solid var(--gold);
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.rekap-card h3 {
  color: var(--brown);
  margin-bottom: 1rem;
  font-size: 1rem;
}
</style>
