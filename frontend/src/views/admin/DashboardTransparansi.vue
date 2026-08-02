<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const loading = ref(true)
const errorMessage = ref('')
const rekapAnggaran = ref(null)
const rekapKegiatan = ref(null)
const pending = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const [a, k, p] = await Promise.all([
      api.get('/admin/pelaporan/rekap-anggaran'),
      api.get('/admin/pelaporan/rekap-kegiatan'),
      api.get('/admin/pelaporan/realisasi-pending')
    ])
    rekapAnggaran.value = a.data
    rekapKegiatan.value = k.data
    pending.value = p.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data transparansi.'
  } finally {
    loading.value = false
  }
})

function fmtRupiah(n) {
  return 'Rp ' + Number(n || 0).toLocaleString('id-ID')
}

function fmtTanggal(iso) {
  if (!iso) return '-'
  const [y, m, d] = iso.split('-')
  const bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
  return `${Number(d)} ${bulan[Number(m) - 1]} ${y}`
}

function barClass(persen) {
  if (persen > 90) return 'serap-merah'
  if (persen >= 70) return 'serap-kuning'
  return 'serap-hijau'
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Dashboard Transparansi Kinerja &amp; Keuangan</h2>
        <p class="greeting">Sistem Perencanaan &amp; Pelaporan — E-Reporting &amp; Budgeting.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="loading" class="greeting">Memuat...</div>

    <template v-else-if="rekapAnggaran">
      <h3 class="section-title">Penyerapan Anggaran {{ rekapAnggaran.tahun }}</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <p class="stat-label">Total Anggaran</p>
          <p class="stat-value">{{ fmtRupiah(rekapAnggaran.total_anggaran) }}</p>
        </div>
        <div class="stat-card">
          <p class="stat-label">Total Realisasi</p>
          <p class="stat-value">{{ fmtRupiah(rekapAnggaran.total_realisasi) }}</p>
        </div>
        <div class="stat-card">
          <p class="stat-label">Persentase Penyerapan</p>
          <p class="stat-value serap-besar" :class="barClass(rekapAnggaran.persen_penyerapan)">
            {{ rekapAnggaran.persen_penyerapan }}%
          </p>
          <div class="serap-bar big">
            <div
              class="serap-fill"
              :class="barClass(rekapAnggaran.persen_penyerapan)"
              :style="{ width: Math.min(100, rekapAnggaran.persen_penyerapan) + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="table-card">
        <h3 class="card-title">Breakdown Penyerapan per Bidang</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Bidang</th>
              <th>Total Anggaran</th>
              <th>Total Realisasi</th>
              <th>Persentase</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in rekapAnggaran.per_bidang" :key="b.bidang_id">
              <td>{{ b.nama_bidang }}</td>
              <td>{{ fmtRupiah(b.total_anggaran) }}</td>
              <td>{{ fmtRupiah(b.total_realisasi) }}</td>
              <td>
                <div class="serap-wrap">
                  <div class="serap-bar">
                    <div class="serap-fill" :class="barClass(b.persen_penyerapan)" :style="{ width: Math.min(100, b.persen_penyerapan) + '%' }"></div>
                  </div>
                  <span class="serap-persen" :class="barClass(b.persen_penyerapan)">{{ b.persen_penyerapan }}%</span>
                </div>
              </td>
            </tr>
            <tr v-if="!rekapAnggaran.per_bidang.length">
              <td colspan="4" class="empty-row">Belum ada alokasi anggaran tahun {{ rekapAnggaran.tahun }}.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="stats-grid">
        <div class="stat-card" @click="router.push({ name: 'admin-kegiatan' })">
          <p class="stat-label">Capaian Pelaksanaan Kegiatan</p>
          <p class="stat-value">
            {{ rekapKegiatan?.jumlah_selesai || 0 }}/{{ rekapKegiatan?.total_direncanakan || 0 }} selesai
          </p>
          <p class="stat-value serap-besar" :class="barClass(rekapKegiatan?.persen_capaian || 0)">
            {{ rekapKegiatan?.persen_capaian || 0 }}%
          </p>
          <div class="serap-bar big">
            <div
              class="serap-fill"
              :class="barClass(rekapKegiatan?.persen_capaian || 0)"
              :style="{ width: Math.min(100, rekapKegiatan?.persen_capaian || 0) + '%' }"
            ></div>
          </div>
        </div>
        <div class="stat-card" @click="router.push({ name: 'admin-realisasi-review' })">
          <p class="stat-label">Realisasi Menunggu Review</p>
          <p class="stat-value">{{ pending.length }}</p>
          <p class="greeting">Klik untuk membuka halaman review.</p>
        </div>
      </div>

      <div class="table-card">
        <h3 class="card-title">Realisasi Diajukan (Menunggu Review)</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Program Kerja</th>
              <th>Tanggal</th>
              <th>Keterangan</th>
              <th>Jumlah</th>
              <th>Diinput Oleh</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in pending" :key="r.id">
              <td>{{ r.judul_program_kerja }}</td>
              <td>{{ fmtTanggal(r.tanggal_realisasi) }}</td>
              <td>{{ r.keterangan }}</td>
              <td>{{ fmtRupiah(r.jumlah_realisasi) }}</td>
              <td>{{ r.nama_diinput }}</td>
            </tr>
            <tr v-if="!pending.length">
              <td colspan="5" class="empty-row">Tidak ada realisasi yang menunggu review.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
