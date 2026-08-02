<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const data = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const tingkatLabels = { kwarcab: 'Kwarcab', kwaran: 'Kwaran', gudep: 'Gudep' }

onMounted(async () => {
  try {
    const res = await api.get('/public/beranda')
    data.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data beranda.'
  } finally {
    loading.value = false
  }
})

function mediaUrl(path) {
  if (!path) return ''
  return `http://localhost:8000${path}`
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso + 'T00:00:00').toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function formatRupiah(angka) {
  return Number(angka || 0).toLocaleString('id-ID')
}
</script>

<template>
  <div class="home-page">
    <section class="home-hero">
      <div class="home-hero-inner">
        <h1>Super Apps Pramuka Jawa Barat</h1>
        <p>
          Platform digital terintegrasi Kwarda Jawa Barat: data keanggotaan,
          program kegiatan, hub wilayah, persuratan, perencanaan &amp; pelaporan,
          hingga marketplace Pramuka.
        </p>
        <div class="home-hero-actions">
          <router-link to="/login" class="btn-primary btn-home-masuk">Masuk</router-link>
          <a href="#berita" class="btn-home-outline">Lihat Kegiatan</a>
        </div>
      </div>
    </section>

    <div v-if="errorMessage" class="alert-error home-alert">{{ errorMessage }}</div>

    <section class="home-section">
      <div class="home-section-head">
        <h2>Statistik Keanggotaan</h2>
        <p>Angka agregat keanggotaan Kwarda Jawa Barat. Detail data individu hanya untuk pengurus yang berwenang.</p>
      </div>
      <div v-if="loading" class="text-muted">Memuat statistik...</div>
      <div v-else-if="data" class="stat-grid">
        <div class="stat-card">
          <span class="stat-value">{{ data.statistik_keanggotaan.total_siaga }}</span>
          <span class="stat-label">Pramuka Siaga</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.statistik_keanggotaan.total_penggalang }}</span>
          <span class="stat-label">Pramuka Penggalang</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.statistik_keanggotaan.total_penegak }}</span>
          <span class="stat-label">Pramuka Penegak</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.statistik_keanggotaan.total_pandega }}</span>
          <span class="stat-label">Pramuka Pandega</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.statistik_keanggotaan.total_dewasa }}</span>
          <span class="stat-label">Pembina / Dewasa</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ data.statistik_keanggotaan.total_gudep }}</span>
          <span class="stat-label">Gugus Depan</span>
        </div>
      </div>
      <p v-if="data && !loading" class="home-footnote">
        Struktur wilayah: {{ data.statistik_keanggotaan.total_kwarcab }} Kwarcab,
        {{ data.statistik_keanggotaan.total_kwaran }} Kwaran,
        {{ data.statistik_keanggotaan.total_gudep }} Gudep.
      </p>
    </section>

    <section id="berita" class="home-section home-section-alt">
      <div class="home-section-head">
        <h2>Berita &amp; Kegiatan Terkini</h2>
        <router-link to="/hub-kegiatan" class="home-section-link">Lihat Semua Berita</router-link>
      </div>
      <div v-if="loading" class="text-muted">Memuat berita...</div>
      <div v-else-if="data && data.berita_terbaru.length" class="card-grid">
        <router-link
          v-for="b in data.berita_terbaru"
          :key="b.id"
          :to="{ name: 'hub-kegiatan-detail', params: { id: b.id } }"
          class="card news-card"
        >
          <div v-if="b.gambar" class="news-thumb">
            <img :src="mediaUrl(b.gambar)" :alt="b.judul" />
          </div>
          <div class="news-body">
            <div class="news-meta">
              <span class="badge-status neutral">{{ tingkatLabels[b.tingkat_wilayah] || b.tingkat_wilayah }} {{ b.nama_wilayah }}</span>
              <span class="text-muted small">{{ formatDate(b.tanggal_kegiatan) }}</span>
            </div>
            <h3 class="card-title">{{ b.judul }}</h3>
            <p class="text-muted news-desc">{{ b.ringkasan }}</p>
          </div>
        </router-link>
      </div>
      <div v-else-if="data" class="text-muted">Belum ada berita yang disetujui.</div>
    </section>

    <section class="home-section">
      <div class="home-section-head">
        <h2>Agenda Mendatang</h2>
        <p>Kegiatan publik terpilih dari Program Kegiatan Internal Kwarda.</p>
      </div>
      <div v-if="loading" class="text-muted">Memuat agenda...</div>
      <div v-else-if="data && data.agenda_mendatang.length" class="agenda-list">
        <div v-for="a in data.agenda_mendatang" :key="a.id" class="agenda-item">
          <div class="agenda-date">
            <strong>{{ new Date(a.tanggal_mulai + 'T00:00:00').toLocaleDateString('id-ID', { day: 'numeric', month: 'short' }) }}</strong>
            <span>{{ new Date(a.tanggal_mulai + 'T00:00:00').getFullYear() }}</span>
          </div>
          <div class="agenda-info">
            <strong>{{ a.judul }}</strong>
            <span v-if="a.lokasi">{{ a.lokasi }}</span>
          </div>
        </div>
      </div>
      <div v-else-if="data" class="text-muted">Belum ada agenda publik terdekat.</div>
    </section>

    <section class="home-section home-section-alt">
      <div class="home-section-head">
        <h2>Marketplace Pramuka</h2>
        <router-link to="/marketplace" class="home-section-link">Lihat Semua Produk</router-link>
      </div>
      <div v-if="loading" class="text-muted">Memuat produk...</div>
      <div v-else-if="data && data.produk_unggulan.length" class="product-grid">
        <router-link
          v-for="p in data.produk_unggulan"
          :key="p.id"
          :to="{ name: 'marketplace-produk', params: { id: p.id } }"
          class="product-card home-product-card"
        >
          <img v-if="p.foto_url" :src="mediaUrl(p.foto_url)" class="product-photo" alt="" />
          <div v-else class="product-photo-placeholder">Foto</div>
          <div class="product-info">
            <span class="toko-nama">{{ p.nama_toko }}</span>
            <h3>{{ p.nama_produk }}</h3>
            <span class="product-harga">Rp {{ formatRupiah(p.harga) }}</span>
          </div>
        </router-link>
      </div>
      <div v-else-if="data" class="text-muted">Belum ada produk aktif.</div>
    </section>

    <section class="home-section">
      <div class="home-section-head">
        <h2>Transparansi Kinerja</h2>
        <p>Akuntabilitas publik penyerapan anggaran Kwarda tahun berjalan.</p>
      </div>
      <div v-if="loading" class="text-muted">Memuat transparansi...</div>
      <div v-else-if="data" class="transparansi-card">
        <div class="transparansi-angka">
          <strong>{{ data.transparansi_ringkas.persen_penyerapan ?? 0 }}%</strong>
          <span>Penyerapan Anggaran {{ data.transparansi_ringkas.tahun }}</span>
        </div>
        <div class="transparansi-bar">
          <div
            class="transparansi-fill"
            :style="{ width: Math.min((data.transparansi_ringkas.persen_penyerapan ?? 0), 100) + '%' }"
          ></div>
        </div>
        <p class="home-footnote">
          Data agregat untuk transparansi publik. Rincian nominal per transaksi dan
          bukti kwitansi bersifat internal.
        </p>
      </div>
    </section>
  </div>
</template>
