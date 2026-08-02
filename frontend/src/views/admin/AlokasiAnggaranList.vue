<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const items = ref([])
const loading = ref(true)
const errorMessage = ref('')

const bidangList = ref([])
const filterTahun = ref('')
const filterBidang = ref('')

const tahunOptions = computed(() => {
  const set = new Set(items.value.map((i) => i.tahun_anggaran))
  set.add(new Date().getFullYear())
  return [...set].sort((a, b) => b - a)
})

onMounted(async () => {
  await loadBidang()
  await loadItems()
})

async function loadBidang() {
  try {
    const res = await api.get('/admin/bidang-kwarda')
    bidangList.value = res.data
  } catch {
    /* optional */
  }
}

async function loadItems() {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {}
    if (filterTahun.value) params.tahun_anggaran = filterTahun.value
    if (filterBidang.value) params.bidang_id = filterBidang.value
    const res = await api.get('/admin/anggaran-program', { params })
    items.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat alokasi anggaran.'
  } finally {
    loading.value = false
  }
}

function barClass(persen) {
  if (persen > 90) return 'serap-merah'
  if (persen >= 70) return 'serap-kuning'
  return 'serap-hijau'
}

function fmtRupiah(n) {
  return 'Rp ' + Number(n || 0).toLocaleString('id-ID')
}

function openDetail(item) {
  router.push({ name: 'admin-anggaran-realisasi', params: { id: item.id } })
}

function openEdit(item) {
  router.push({ name: 'admin-anggaran-alokasi-baru', query: { edit: item.id } })
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>Alokasi Anggaran Program</h2>
        <p class="greeting">Alokasi anggaran per program kerja per tahun, beserta penyerapannya.</p>
      </div>
      <router-link to="/admin/anggaran-alokasi/baru" class="btn-primary btn-add">
        + Alokasikan Anggaran Baru
      </router-link>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card">
      <div class="filters-bar">
        <select v-model="filterTahun" @change="loadItems">
          <option value="">Semua Tahun</option>
          <option v-for="t in tahunOptions" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="filterBidang" @change="loadItems">
          <option value="">Semua Bidang</option>
          <option v-for="b in bidangList" :key="b.id" :value="b.id">{{ b.nama_bidang }}</option>
        </select>
      </div>

      <div v-if="loading" class="greeting">Memuat...</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Program Kerja</th>
            <th>Bidang</th>
            <th>Tahun</th>
            <th>Jumlah Anggaran</th>
            <th>Total Realisasi</th>
            <th>Penyerapan</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.judul_program_kerja }}</td>
            <td>{{ item.nama_bidang }}</td>
            <td>{{ item.tahun_anggaran }}</td>
            <td>{{ fmtRupiah(item.jumlah_anggaran) }}</td>
            <td>{{ fmtRupiah(item.total_realisasi) }}</td>
            <td>
              <div class="serap-wrap">
                <div class="serap-bar">
                  <div class="serap-fill" :class="barClass(item.persen_penyerapan)" :style="{ width: Math.min(100, item.persen_penyerapan) + '%' }"></div>
                </div>
                <span class="serap-persen" :class="barClass(item.persen_penyerapan)">{{ item.persen_penyerapan }}%</span>
              </div>
            </td>
            <td>
              <div class="action-cell">
                <button class="btn-small" @click="openDetail(item)">Realisasi</button>
                <button class="btn-small" @click="openEdit(item)">Edit</button>
              </div>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="7" class="empty-row">Belum ada alokasi anggaran.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
