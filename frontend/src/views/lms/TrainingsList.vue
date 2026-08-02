<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import lmsService from '../../services/lms'

const router = useRouter()

const trainings = ref([])
const loading = ref(true)
const error = ref('')

// Search & Pagination state
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const LIMIT = 6

let searchTimer = null

onMounted(() => {
  fetchTrainings()
})

// Debounced search — reset to page 1 on new search
watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchTrainings()
  }, 400)
})

async function fetchTrainings() {
  loading.value = true
  error.value = ''
  try {
    const res = await lmsService.getTrainings({
      search: searchQuery.value,
      page: currentPage.value,
      limit: LIMIT
    })
    trainings.value = res.data.items
    totalPages.value = res.data.total_pages
    totalItems.value = res.data.total
  } catch (err) {
    error.value = err.response?.data?.detail || 'Gagal memuat daftar pelatihan'
  } finally {
    loading.value = false
  }
}

function goToPage(page) {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchTrainings()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: 'numeric', month: 'long', year: 'numeric'
  })
}

function getPageNumbers() {
  const pages = []
  const delta = 2
  const left = Math.max(1, currentPage.value - delta)
  const right = Math.min(totalPages.value, currentPage.value + delta)

  if (left > 1) { pages.push(1); if (left > 2) pages.push('...') }
  for (let i = left; i <= right; i++) pages.push(i)
  if (right < totalPages.value) { if (right < totalPages.value - 1) pages.push('...'); pages.push(totalPages.value) }
  return pages
}
</script>

<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Katalog e-Pelatihan</h2>
        <p class="page-subtitle">Tingkatkan kompetensi Pramuka Anda melalui modul pembelajaran mandiri yang interaktif.</p>
      </div>

      <!-- Search Bar -->
      <div class="search-wrap">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Cari judul pelatihan..."
            id="search-training"
          />
          <button v-if="searchQuery" @click="searchQuery = ''" class="clear-btn" title="Hapus pencarian">
            &times;
          </button>
        </div>
      </div>
    </div>

    <!-- Result Info -->
    <div v-if="!loading && !error" class="result-info">
      <span v-if="searchQuery">
        Menampilkan <strong>{{ totalItems }}</strong> hasil untuk "<em>{{ searchQuery }}</em>"
      </span>
      <span v-else>
        <strong>{{ totalItems }}</strong> pelatihan tersedia
      </span>
    </div>

    <!-- State: Loading -->
    <div v-if="loading" class="state-center">
      <div class="spinner"></div>
      <p class="state-text">Memuat katalog pelatihan...</p>
    </div>

    <!-- State: Error -->
    <div v-else-if="error" class="state-error">
      {{ error }}
    </div>

    <!-- State: Empty -->
    <div v-else-if="trainings.length === 0" class="state-empty">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
        </svg>
      </div>
      <h3>{{ searchQuery ? 'Pelatihan tidak ditemukan' : 'Belum ada pelatihan' }}</h3>
      <p>{{ searchQuery ? `Tidak ada pelatihan dengan judul "${searchQuery}"` : 'Silakan kembali lagi nanti.' }}</p>
      <button v-if="searchQuery" @click="searchQuery = ''" class="empty-clear-btn">Tampilkan Semua</button>
    </div>
    
    <!-- Grid -->
    <div v-else class="card-grid">
      <div v-for="(training, index) in trainings" :key="training.id" 
           class="training-card"
           :style="`animation-delay: ${index * 0.06}s`">
        
        <div class="card-badge">LMS PROGRAM</div>
        
        <h3 class="card-title">{{ training.title }}</h3>
        
        <p class="card-desc">
          {{ training.description || 'Pelatihan ini tidak memiliki deskripsi khusus. Silakan masuk untuk melihat detail modul.' }}
        </p>
        
        <div class="card-meta">
          <div class="meta-row">
            <span class="meta-label">Mulai</span>
            <span class="meta-value">{{ formatDate(training.start_date) }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">KKM</span>
            <span class="meta-value">{{ training.passing_grade }} Poin</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">Status</span>
            <span :class="['meta-status', training.status === 'Published' ? 'status-pub' : 'status-draft']">
              {{ training.status === 'Published' ? 'Tersedia' : 'Draft' }}
            </span>
          </div>
        </div>
        
        <router-link :to="{ name: 'lms-training-detail', params: { id: training.id } }" class="card-btn">
          Lihat Detail Modul &rarr;
        </router-link>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && !error && totalPages > 1" class="pagination">
      <!-- Prev -->
      <button class="page-btn nav-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
        &larr;
      </button>

      <!-- Page numbers -->
      <template v-for="p in getPageNumbers()" :key="p">
        <span v-if="p === '...'" class="page-ellipsis">...</span>
        <button v-else
          :class="['page-btn', currentPage === p ? 'page-active' : '']"
          @click="goToPage(p)">
          {{ p }}
        </button>
      </template>

      <!-- Next -->
      <button class="page-btn nav-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
        &rarr;
      </button>
    </div>

    <!-- Page info -->
    <p v-if="!loading && !error && totalPages > 1" class="page-info">
      Halaman {{ currentPage }} dari {{ totalPages }}
    </p>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  min-height: 80vh;
}

/* Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-bottom: 1.25rem;
  animation: fadeDown 0.5s ease-out;
}
@media (min-width: 768px) {
  .page-header { flex-direction: row; align-items: flex-end; justify-content: space-between; }
}
.page-title {
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  font-weight: 800;
  background: linear-gradient(135deg, var(--brown), var(--gold));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.35rem;
  line-height: 1.2;
}
.page-subtitle { color: #6b7280; font-size: 0.9rem; margin: 0; }

/* Search */
.search-wrap { flex-shrink: 0; }
.search-box {
  display: flex; align-items: center;
  background: white; border: 2px solid #f0ebe4;
  border-radius: 14px; padding: 0 0.875rem;
  width: 100%; min-width: 280px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-box:focus-within {
  border-color: var(--gold);
  box-shadow: 0 2px 14px rgba(212, 172, 13, 0.15);
}
.search-icon { width: 18px; height: 18px; color: #9ca3af; flex-shrink: 0; }
.search-input {
  flex: 1; border: none; outline: none;
  padding: 0.7rem 0.5rem; font-size: 0.9rem;
  background: transparent; color: #374151;
  font-family: inherit;
}
.search-input::placeholder { color: #9ca3af; }
.clear-btn {
  background: none; border: none; cursor: pointer;
  color: #9ca3af; font-size: 1.2rem; padding: 0;
  line-height: 1; transition: color 0.2s;
}
.clear-btn:hover { color: var(--maroon); }

/* Result info */
.result-info {
  font-size: 0.85rem; color: #6b7280;
  margin-bottom: 1.25rem;
}
.result-info strong { color: #374151; }
.result-info em { color: var(--brown); font-style: normal; font-weight: 600; }

/* States */
.state-center {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 1rem; padding: 4rem 2rem;
}
.state-text { color: #6b7280; font-weight: 500; }
.spinner {
  width: 52px; height: 52px;
  border: 4px solid #e5e7eb;
  border-top-color: var(--gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.state-error {
  background: #fef2f2; color: #dc2626;
  border: 1px solid #fecaca; border-radius: 12px;
  padding: 1.5rem; text-align: center;
}
.state-empty {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; padding: 4rem 2rem;
  background: white; border-radius: 24px;
  border: 2px dashed #e5e7eb;
  gap: 0.75rem;
}
.empty-icon { width: 56px; height: 56px; color: #d1d5db; }
.empty-icon svg { width: 100%; height: 100%; }
.state-empty h3 { font-size: 1.2rem; font-weight: 700; color: #374151; margin: 0; }
.state-empty p { color: #9ca3af; font-size: 0.9rem; margin: 0; }
.empty-clear-btn {
  margin-top: 0.5rem; padding: 0.6rem 1.5rem;
  background: var(--brown); color: white;
  border: none; border-radius: 10px;
  font-size: 0.875rem; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
}
.empty-clear-btn:hover { background: var(--brown-dark); }

/* Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

/* Card */
.training-card {
  background: white; border-radius: 20px;
  padding: 1.75rem; border: 1px solid #f0ebe4;
  box-shadow: 0 4px 20px rgba(92, 64, 51, 0.06);
  display: flex; flex-direction: column; gap: 0.75rem;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  animation: fadeUp 0.4s ease-out both;
  position: relative; overflow: hidden;
}
.training-card::before {
  content: '';
  position: absolute; top: -40px; right: -40px;
  width: 120px; height: 120px;
  background: radial-gradient(circle, rgba(212, 172, 13, 0.12) 0%, transparent 70%);
  border-radius: 50%; transition: transform 0.4s ease;
  pointer-events: none;
}
.training-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(92, 64, 51, 0.14); }
.training-card:hover::before { transform: scale(1.6); }

.card-badge {
  display: inline-flex; align-items: center;
  padding: 0.25rem 0.75rem;
  background: #faf6f0; color: var(--brown);
  font-size: 0.65rem; font-weight: 700;
  letter-spacing: 0.08em; border-radius: 999px;
  width: fit-content; border: 1px solid rgba(92, 64, 51, 0.12);
}
.card-title {
  font-size: 1.15rem; font-weight: 700;
  color: #1f2937; line-height: 1.4; margin: 0;
  transition: color 0.2s;
}
.training-card:hover .card-title { color: var(--maroon); }
.card-desc {
  font-size: 0.875rem; color: #6b7280;
  line-height: 1.6; flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  background: #fafafa; border: 1px solid #f0ebe4;
  border-radius: 12px; padding: 0.875rem 1rem;
  display: flex; flex-direction: column; gap: 0.5rem;
}
.meta-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.825rem;
}
.meta-label { color: var(--gold); font-weight: 600; }
.meta-value { color: #374151; font-weight: 600; }
.meta-status { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
.status-pub { background: #f0fdf4; color: #16a34a; }
.status-draft { background: #fefce8; color: #ca8a04; }

.card-btn {
  display: block; text-align: center;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, var(--brown), var(--brown-dark));
  color: white; font-size: 0.875rem; font-weight: 600;
  border-radius: 12px; text-decoration: none;
  transition: all 0.2s ease; margin-top: auto;
}
.card-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(92, 64, 51, 0.3); }

/* Pagination */
.pagination {
  display: flex; justify-content: center; align-items: center;
  gap: 0.4rem; flex-wrap: wrap; margin-top: 0.5rem;
}
.page-btn {
  min-width: 40px; height: 40px; padding: 0 0.75rem;
  border: 2px solid #e5e7eb; background: white;
  border-radius: 10px; font-size: 0.9rem;
  font-weight: 600; color: #374151; cursor: pointer;
  transition: all 0.18s ease; font-family: inherit;
  display: flex; align-items: center; justify-content: center;
}
.page-btn:hover:not(:disabled) {
  border-color: var(--gold); color: var(--brown);
  background: #faf6f0;
}
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-active {
  background: var(--brown) !important;
  border-color: var(--brown) !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(92, 64, 51, 0.25);
}
.nav-btn { font-size: 1rem; }
.page-ellipsis {
  display: flex; align-items: center; justify-content: center;
  width: 36px; color: #9ca3af; font-weight: 600;
}
.page-info {
  text-align: center; margin-top: 0.75rem;
  font-size: 0.8rem; color: #9ca3af;
}

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-16px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .page-container { padding: 1.25rem 1rem; }
  .card-grid { grid-template-columns: 1fr; }
  .search-box { min-width: unset; }
}
</style>
