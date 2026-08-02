<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const rekapJenjang = ref([])
const rekapWilayah = ref([])
const rekapKompetensi = ref([])
const rekapCapaian = ref([])

const jenjangLabels = { siaga: 'Siaga', penggalang: 'Penggalang', penegak: 'Penegak', pandega: 'Pandega', dewasa: 'Dewasa' }

onMounted(async () => {
  try {
    const [jenjang, wilayah, kompetensi, capaian] = await Promise.all([
      api.get('/rekap/anggota/jenjang'),
      api.get('/rekap/anggota/kota-kabupaten'),
      api.get('/rekap/kompetensi/jenjang'),
      api.get('/rekap/capaian/jenjang')
    ])
    rekapJenjang.value = jenjang.data
    rekapWilayah.value = wilayah.data
    rekapKompetensi.value = kompetensi.data
    rekapCapaian.value = capaian.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat rekap.'
  } finally {
    loading.value = false
  }
})

function totalRekap(list) {
  return list.reduce((acc, item) => acc + (item.jumlah || 0), 0)
}

function exportCsv(name, headers, rows) {
  const csv = [headers.join(','), ...rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${name}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

function exportRekapJenjang() {
  exportCsv('rekap_per_jenjang', ['Jenjang', 'Jumlah'], rekapJenjang.value.map((i) => [jenjangLabels[i.jenjang] || i.jenjang, i.jumlah]))
}

function exportRekapWilayah() {
  exportCsv('rekap_per_kota_kabupaten', ['Kota/Kabupaten', 'Jumlah'], rekapWilayah.value.map((i) => [i.kota_kabupaten, i.jumlah]))
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Rekapitulasi &amp; Laporan</h2>
        <p class="greeting">Rekap data keanggotaan dan kompetensi.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="rekap-grid" v-if="!loading">
      <div class="rekap-card">
        <div class="card-head">
          <h3>Rekap Anggota per Jenjang</h3>
          <button class="btn-small" @click="exportRekapJenjang">Ekspor CSV</button>
        </div>
        <table class="data-table">
          <thead><tr><th>Jenjang</th><th>Jumlah</th></tr></thead>
          <tbody>
            <tr v-for="item in rekapJenjang" :key="item.jenjang">
              <td>{{ jenjangLabels[item.jenjang] || item.jenjang }}</td>
              <td>{{ item.jumlah }}</td>
            </tr>
            <tr v-if="rekapJenjang.length === 0"><td colspan="2" class="empty-row">Belum ada data.</td></tr>
            <tr v-if="rekapJenjang.length > 0"><td><strong>Total</strong></td><td><strong>{{ totalRekap(rekapJenjang) }}</strong></td></tr>
          </tbody>
        </table>
      </div>

      <div class="rekap-card">
        <div class="card-head">
          <h3>Rekap Anggota per Kota/Kabupaten</h3>
          <button class="btn-small" @click="exportRekapWilayah">Ekspor CSV</button>
        </div>
        <table class="data-table">
          <thead><tr><th>Kota/Kabupaten</th><th>Jumlah</th></tr></thead>
          <tbody>
            <tr v-for="item in rekapWilayah" :key="item.kota_kabupaten">
              <td>{{ item.kota_kabupaten }}</td>
              <td>{{ item.jumlah }}</td>
            </tr>
            <tr v-if="rekapWilayah.length === 0"><td colspan="2" class="empty-row">Belum ada data.</td></tr>
          </tbody>
        </table>
      </div>

      <div class="rekap-card">
        <h3>Master Kompetensi per Jenjang</h3>
        <table class="data-table">
          <thead><tr><th>Jenjang</th><th>Jumlah Kompetensi</th></tr></thead>
          <tbody>
            <tr v-for="item in rekapKompetensi" :key="item.jenjang">
              <td>{{ jenjangLabels[item.jenjang] || item.jenjang }}</td>
              <td>{{ item.jumlah }}</td>
            </tr>
            <tr v-if="rekapKompetensi.length === 0"><td colspan="2" class="empty-row">Belum ada data.</td></tr>
          </tbody>
        </table>
      </div>

      <div class="rekap-card">
        <h3>Capaian Kompetensi per Jenjang</h3>
        <table class="data-table">
          <thead><tr><th>Jenjang</th><th>Jumlah Capaian</th></tr></thead>
          <tbody>
            <tr v-for="item in rekapCapaian" :key="item.jenjang">
              <td>{{ jenjangLabels[item.jenjang] || item.jenjang }}</td>
              <td>{{ item.jumlah }}</td>
            </tr>
            <tr v-if="rekapCapaian.length === 0"><td colspan="2" class="empty-row">Belum ada data.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-else class="greeting">Memuat data...</p>
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

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.card-head h3 {
  margin-bottom: 0;
}
</style>
