<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const user = ref(null)
const stats = ref([
  { label: 'Total User', value: '...' },
  { label: 'Total Anggota', value: 0 },
  { label: 'Program Kerja Berjalan', value: 0 },
  { label: 'Total Program Kerja', value: 0 }
])

const kegiatanMendatang = ref([])
const programBerjalan = ref(0)
const disposisiMenunggu = ref(0)
const suratSegeraBaru = ref(0)
const anggaranPersen = ref(0)
const realisasiPending = ref(0)

onMounted(async () => {
  try {
    const res = await api.get('/auth/me')
    user.value = res.data
  } catch {
    /* akan di-handle guard/logout di layout */
  }

  try {
    const usersRes = await api.get('/admin/users')
    stats.value[0].value = usersRes.data.length
  } catch {
    /* abaikan jika gagal */
  }

  try {
    const anggotaRes = await api.get('/admin/anggota/statistik')
    stats.value[1].value = anggotaRes.data.total
  } catch {
    /* abaikan jika gagal */
  }

  try {
    const rekapRes = await api.get('/admin/program-kerja/rekap')
    programBerjalan.value = rekapRes.data.per_status.berjalan
    stats.value[2].value = rekapRes.data.per_status.berjalan
    stats.value[3].value = rekapRes.data.total
  } catch {
    /* abaikan jika gagal */
  }

  try {
    const mendatangRes = await api.get('/admin/kegiatan/mendatang?limit=5')
    kegiatanMendatang.value = mendatangRes.data
  } catch {
    /* abaikan jika gagal */
  }

  try {
    const rekapPersuratanRes = await api.get('/admin/persuratan/rekap')
    disposisiMenunggu.value = rekapPersuratanRes.data.disposisi_menunggu_saya
    suratSegeraBaru.value = rekapPersuratanRes.data.surat_segera_baru
  } catch {
    /* abaikan jika gagal */
  }

  try {
    const rekapAnggaranRes = await api.get('/admin/pelaporan/rekap-anggaran')
    anggaranPersen.value = rekapAnggaranRes.data.persen_penyerapan
    const pendingRes = await api.get('/admin/pelaporan/realisasi-pending')
    realisasiPending.value = pendingRes.data.length
  } catch {
    /* abaikan jika gagal */
  }
})

function fmtTanggal(tgl) {
  if (!tgl) return '-'
  const parts = tgl.split('-')
  const bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  return `${Number(parts[2])} ${bulan[Number(parts[1]) - 1]} ${parts[0]}`
}
</script>

<template>
  <div class="dashboard-content">
    <h2 v-if="user">Selamat datang, {{ user.nama_lengkap }}!</h2>
    <h2 v-else>Memuat...</h2>
    <p class="greeting">Ringkasan data Super Apps Pramuka Jawa Barat.</p>

    <div class="card-grid">
      <div v-for="stat in stats" :key="stat.label" class="stat-card">
        <span class="stat-value">{{ stat.value }}</span>
        <span class="stat-label">{{ stat.label }}</span>
      </div>
    </div>

    <div class="dashboard-columns">
      <section class="stat-card wide dashboard-section">
        <h3>Kegiatan Mendatang</h3>
        <div v-if="kegiatanMendatang.length">
          <ul class="kegiatan-mendatang-list">
            <li v-for="k in kegiatanMendatang" :key="k.id">
              <div class="km-item">
                <span class="km-tanggal">{{ fmtTanggal(k.tanggal_mulai) }}</span>
                <span class="km-judul">{{ k.judul }}</span>
                <span
                  class="badge"
                  :class="{ 'badge-status-rencana': k.status === 'rencana', 'badge-status-berjalan': k.status === 'berjalan' }"
                >
                  {{ k.status }}
                </span>
              </div>
              <span class="km-lokasi">{{ k.lokasi || 'lokasi belum diisi' }}</span>
            </li>
          </ul>
        </div>
        <p v-else class="greeting">Tidak ada kegiatan mendatang.</p>
        <router-link to="/admin/kegiatan" class="btn-small link-inline">Kelola Kegiatan &rarr;</router-link>
      </section>

      <section class="stat-card wide dashboard-section">
        <h3>Program Kerja Berjalan</h3>
        <p class="rekap-besar">{{ programBerjalan }} program</p>
        <router-link to="/admin/program-kerja" class="btn-small link-inline">Lihat Program Kerja &rarr;</router-link>
      </section>

      <section class="stat-card wide dashboard-section">
        <h3>Sistem Persuratan</h3>
        <p class="rekap-besar">{{ disposisiMenunggu }} disposisi menunggu tindak lanjut</p>
        <p v-if="suratSegeraBaru" class="greeting urgent-text">{{ suratSegeraBaru }} surat masuk bersifat segera belum didisposisikan.</p>
        <router-link to="/admin/disposisi-saya" class="btn-small link-inline">Buka Disposisi Saya &rarr;</router-link>
      </section>

      <section class="stat-card wide dashboard-section">
        <h3>Transparansi Anggaran</h3>
        <p class="rekap-besar">{{ anggaranPersen }}% penyerapan anggaran tahun berjalan</p>
        <p v-if="realisasiPending" class="greeting">{{ realisasiPending }} realisasi menunggu review admin.</p>
        <router-link to="/admin/dashboard-transparansi" class="btn-small link-inline">Buka Dashboard Transparansi &rarr;</router-link>
      </section>
    </div>
  </div>
</template>
