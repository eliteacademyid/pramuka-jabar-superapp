<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import QRCode from 'qrcode'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const anggotaList = ref([])
const ktaList = ref([])
const selectedKta = ref(null)
const showModal = ref(false)
const qrDataUrl = ref('')

const jenjangLabels = { siaga: 'Siaga', penggalang: 'Penggalang', penegak: 'Penegak', pandega: 'Pandega', dewasa: 'Dewasa' }

const ktaByAnggota = computed(() => {
  const map = {}
  for (const k of ktaList.value) map[k.anggota_id] = k
  return map
})

async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [anggota, kta] = await Promise.all([
      api.get('/anggota/'),
      api.get('/kta/')
    ])
    anggotaList.value = anggota.data
    ktaList.value = kta.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data anggota.'
  } finally {
    loading.value = false
  }
}

async function generateKta(anggota) {
  errorMessage.value = ''
  try {
    const res = await api.post(`/kta/generate/${anggota.id}`)
    const kta = res.data
    await loadData()
    await showCard(kta.id)
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal membuat e-KTA.'
  }
}

async function showCard(ktaId) {
  const kta = ktaList.value.find((k) => k.id === ktaId)
  if (!kta) return
  selectedKta.value = kta
  showModal.value = true
  await nextTick()
  try {
    qrDataUrl.value = await QRCode.toDataURL(kta.qr_data || kta.nomor_kta, {
      width: 120,
      margin: 1,
      color: { dark: '#1a3c1a', light: '#ffffff' }
    })
  } catch {
    qrDataUrl.value = ''
  }
}

function formatDate(dt) {
  if (!dt) return '-'
  const d = new Date(dt)
  return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })
}

function hasKta(anggota) {
  return !!ktaByAnggota.value[anggota.id]
}

function printCard() {
  const printWindow = window.open('', '_blank')
  const k = selectedKta.value
  const html = `
    <html><head><title>e-KTA ${k.nama_lengkap}</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body { font-family: 'Segoe UI', Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #f0ede6; }
      .card { width: 540px; height: 340px; border-radius: 14px; overflow: hidden; border: 2px solid #8a5a2b; box-shadow: 0 4px 16px rgba(0,0,0,0.2); display: flex; flex-direction: column; background: linear-gradient(135deg, #fdf6e3 0%, #f5e8c8 100%); position: relative; }
      .band { background: linear-gradient(90deg, #1a3c1a, #2e5e2e); color: #ffd700; text-align: center; padding: 8px; font-size: 14px; font-weight: bold; letter-spacing: 1px; }
      .body { display: flex; padding: 16px 18px; flex: 1; }
      .left { width: 150px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-right: 2px dashed #c9a24b; margin-right: 16px; padding-right: 16px; }
      .avatar { width: 96px; height: 96px; border-radius: 50%; background: #2e5e2e; color: #ffd700; font-size: 34px; font-weight: bold; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
      .qrcode { width: 96px; height: 96px; }
      .right { flex: 1; }
      .right h1 { font-size: 20px; color: #1a3c1a; margin-bottom: 6px; }
      .field { display: flex; font-size: 12px; margin-bottom: 4px; }
      .field .label { width: 108px; color: #7a5c1e; font-weight: bold; }
      .field .val { flex: 1; color: #222; }
      .footer { background: #1a3c1a; color: #ffd700; text-align: center; padding: 7px; font-size: 11px; font-weight: bold; }
    </style></head><body>
    <div class="card">
      <div class="band">GERAKAN PRAMUKA KWARDA JAWA BARAT &mdash; e-KTA</div>
      <div class="body">
        <div class="left">
          <div class="avatar">${(k.nama_lengkap || '?').charAt(0).toUpperCase()}</div>
          <img class="qrcode" src="${qrDataUrl.value}" />
        </div>
        <div class="right">
          <h1>${k.nama_lengkap || ''}</h1>
          <div class="field"><span class="label">Nomor KTA</span><span class="val">${k.nomor_kta}</span></div>
          <div class="field"><span class="label">NTA</span><span class="val">${k.nta || '-'}</span></div>
          <div class="field"><span class="label">Jenjang</span><span class="val">${jenjangLabels[k.jenjang] || k.jenjang || '-'}</span></div>
          <div class="field"><span class="label">Gugus Depan</span><span class="val">${k.gudep || '-'}</span></div>
          <div class="field"><span class="label">Kwarran</span><span class="val">${k.kwarran || '-'}</span></div>
          <div class="field"><span class="label">Kwarcab</span><span class="val">${k.kwarcab || '-'}</span></div>
          <div class="field"><span class="label">Alamat</span><span class="val">${k.alamat || '-'}</span></div>
        </div>
      </div>
      <div class="footer">Berlaku s.d. ${formatDate(k.tanggal_berlaku)} &mdash; ${k.status.toUpperCase()}</div>
    </div>
    <script>window.onload = () => { setTimeout(() => { window.print() }, 300) }<\/script>
    </body></html>`
  printWindow.document.write(html)
  printWindow.document.close()
}

onMounted(loadData)
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>e-KTA Anggota</h2>
        <p class="greeting">Kelola dan cetak Kartu Tanda Anggota elektronik.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="toolbar">
      <button class="btn-small" @click="loadData">Muat Ulang</button>
    </div>

    <table class="data-table" v-if="!loading">
      <thead>
        <tr>
          <th>Nama</th>
          <th>NTA</th>
          <th>Jenjang</th>
          <th>Gudep</th>
          <th>Nomor KTA</th>
          <th>Masa Berlaku</th>
          <th class="ta-right">Aksi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="anggota in anggotaList" :key="anggota.id">
          <td>{{ anggota.nama_lengkap }}</td>
          <td>{{ anggota.nta }}</td>
          <td>{{ jenjangLabels[anggota.jenjang] || anggota.jenjang }}</td>
          <td>{{ anggota.gudep?.nama || '-' }}</td>
          <td>{{ ktaByAnggota[anggota.id]?.nomor_kta || '-' }}</td>
          <td>{{ ktaByAnggota[anggota.id] ? formatDate(ktaByAnggota[anggota.id].tanggal_berlaku) : '-' }}</td>
          <td class="ta-right">
            <template v-if="hasKta(anggota)">
              <button class="btn-small" @click="showCard(ktaByAnggota[anggota.id].id)">Lihat Kartu</button>
            </template>
            <template v-else>
              <button class="btn-small btn-primary" @click="generateKta(anggota)">Generate e-KTA</button>
            </template>
          </td>
        </tr>
        <tr v-if="anggotaList.length === 0"><td colspan="7" class="empty-row">Belum ada data anggota.</td></tr>
      </tbody>
    </table>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showModal && selectedKta" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <div class="modal-head">
          <h3>e-KTA — {{ selectedKta.nama_lengkap }}</h3>
          <button class="modal-close" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="kta-card">
            <div class="kta-band">GERAKAN PRAMUKA KWARDA JAWA BARAT — e-KTA</div>
            <div class="kta-body">
              <div class="kta-left">
                <div class="kta-avatar">{{ (selectedKta.nama_lengkap || '?').charAt(0).toUpperCase() }}</div>
                <img v-if="qrDataUrl" class="kta-qr" :src="qrDataUrl" alt="QR Code" />
              </div>
              <div class="kta-right">
                <h1>{{ selectedKta.nama_lengkap }}</h1>
                <div class="kta-field"><span class="kta-label">Nomor KTA</span><span>{{ selectedKta.nomor_kta }}</span></div>
                <div class="kta-field"><span class="kta-label">NTA</span><span>{{ selectedKta.nta || '-' }}</span></div>
                <div class="kta-field"><span class="kta-label">Jenjang</span><span>{{ jenjangLabels[selectedKta.jenjang] || selectedKta.jenjang }}</span></div>
                <div class="kta-field"><span class="kta-label">Gugus Depan</span><span>{{ selectedKta.gudep || '-' }}</span></div>
                <div class="kta-field"><span class="kta-label">Kwarran</span><span>{{ selectedKta.kwarran || '-' }}</span></div>
                <div class="kta-field"><span class="kta-label">Kwarcab</span><span>{{ selectedKta.kwarcab || '-' }}</span></div>
                <div class="kta-field"><span class="kta-label">Alamat</span><span>{{ selectedKta.alamat || '-' }}</span></div>
              </div>
            </div>
            <div class="kta-footer">Berlaku s.d. {{ formatDate(selectedKta.tanggal_berlaku) }} — {{ selectedKta.status.toUpperCase() }}</div>
          </div>
          <div class="modal-actions">
            <button class="btn-small" @click="printCard">Cetak</button>
            <button class="btn-small" @click="showModal = false">Tutup</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  margin: 1rem 0;
  display: flex;
  justify-content: flex-end;
}

.btn-primary {
  background: var(--brown);
  color: #fff;
}

.ta-right {
  text-align: right;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--white);
  border: 2px solid var(--gold);
  border-radius: 12px;
  max-width: 640px;
  width: 95%;
  max-height: 90vh;
  overflow: auto;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e5dcc5;
}

.modal-head h3 {
  color: var(--brown);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--brown);
  cursor: pointer;
}

.modal-body {
  padding: 1.25rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.kta-card {
  width: 540px;
  max-width: 100%;
  height: 340px;
  border-radius: 14px;
  overflow: hidden;
  border: 2px solid #8a5a2b;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #fdf6e3 0%, #f5e8c8 100%);
}

.kta-band {
  background: linear-gradient(90deg, #1a3c1a, #2e5e2e);
  color: #ffd700;
  text-align: center;
  padding: 8px;
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 1px;
}

.kta-body {
  display: flex;
  padding: 16px 18px;
  flex: 1;
}

.kta-left {
  width: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 2px dashed #c9a24b;
  margin-right: 16px;
  padding-right: 16px;
}

.kta-avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: #2e5e2e;
  color: #ffd700;
  font-size: 34px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.kta-qr {
  width: 96px;
  height: 96px;
}

.kta-right {
  flex: 1;
}

.kta-right h1 {
  font-size: 20px;
  color: #1a3c1a;
  margin-bottom: 6px;
}

.kta-field {
  display: flex;
  font-size: 12px;
  margin-bottom: 4px;
}

.kta-label {
  width: 108px;
  color: #7a5c1e;
  font-weight: bold;
}

.kta-footer {
  background: #1a3c1a;
  color: #ffd700;
  text-align: center;
  padding: 7px;
  font-size: 11px;
  font-weight: bold;
}
</style>
