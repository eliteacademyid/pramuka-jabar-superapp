<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import lmsService from '../../services/lms'

const router = useRouter()
const user = ref(null)
const totalUsers = ref(0)
const totalTrainings = ref(0)
const totalEnrollments = ref(0)
const recentEnrollments = ref([])
const trainings = ref([])
const loading = ref(true)

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return 'Selamat Pagi'
  if (hour < 15) return 'Selamat Siang'
  if (hour < 18) return 'Selamat Sore'
  return 'Selamat Malam'
})

const today = computed(() =>
  new Date().toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
)

onMounted(async () => {
  try {
    const [meRes] = await Promise.all([api.get('/auth/me')])
    user.value = meRes.data
  } catch {}

  if (user.value?.role === 'admin') {
    await loadAdminStats()
  } else {
    await loadStaffStats()
  }
  loading.value = false
})

async function loadAdminStats() {
  try {
    const [usersRes, trainingsRes] = await Promise.all([
      api.get('/admin/users'),
      lmsService.getTrainings({ limit: 100 })
    ])
    totalUsers.value = usersRes.data.length
    totalTrainings.value = trainingsRes.data.total || 0
    trainings.value = (trainingsRes.data.items || []).slice(0, 4)
  } catch {}
}

async function loadStaffStats() {
  try {
    const [enrollRes, trainingsRes] = await Promise.all([
      lmsService.getMyEnrollments(),
      lmsService.getTrainings({ limit: 4 })
    ])
    recentEnrollments.value = enrollRes.data.slice(0, 3)
    totalEnrollments.value = enrollRes.data.length
    trainings.value = trainingsRes.data.items || []
  } catch {}
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<template>
  <div class="dashboard">

    <!-- Hero Banner -->
    <div class="hero-banner">
      <div class="hero-deco hero-deco-1"></div>
      <div class="hero-deco hero-deco-2"></div>
      <div class="hero-content">
        <div class="hero-text">
          <p class="hero-date">{{ today }}</p>
          <h1 class="hero-greeting">
            {{ greeting }},<br>
            <span class="hero-name">{{ user?.nama_lengkap || '...' }}</span>
          </h1>
          <p class="hero-subtitle">
            {{ user?.role === 'admin'
              ? 'Kelola pelatihan dan pengguna Super Apps Pramuka Jawa Barat.'
              : 'Tingkatkan kompetensi Anda melalui e-Pelatihan Kwarcab KBB.'
            }}
          </p>
          <div class="hero-actions">
            <router-link v-if="user?.role === 'admin'" to="/admin/manage-trainings" class="hero-btn hero-btn-primary">
              Kelola Pelatihan
            </router-link>
            <router-link v-else to="/admin/trainings" class="hero-btn hero-btn-primary">
              Mulai Belajar
            </router-link>
            <router-link v-if="user?.role !== 'admin'" to="/admin/enrollments" class="hero-btn hero-btn-ghost">
              Pelatihanku
            </router-link>
            <router-link v-else to="/admin/users" class="hero-btn hero-btn-ghost">
              Manajemen User
            </router-link>
          </div>
        </div>
        <div class="hero-logo-wrap">
          <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Lambang_Pramuka.svg/1200px-Lambang_Pramuka.svg.png"
               alt="Logo Pramuka" class="hero-logo" />
        </div>
      </div>
    </div>

    <!-- Stats Cards (Admin) -->
    <div v-if="user?.role === 'admin'" class="stats-row">
      <div class="stat-card" style="--c: #6366f1; --cb: #ede9fe;">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-val">{{ totalUsers }}</span>
          <span class="stat-lbl">Total Pengguna</span>
        </div>
        <router-link to="/admin/users" class="stat-link">Lihat &rarr;</router-link>
      </div>

      <div class="stat-card" style="--c: #f59e0b; --cb: #fef3c7;">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-val">{{ totalTrainings }}</span>
          <span class="stat-lbl">Total Pelatihan</span>
        </div>
        <router-link to="/admin/manage-trainings" class="stat-link">Lihat &rarr;</router-link>
      </div>

      <div class="stat-card" style="--c: #10b981; --cb: #d1fae5;">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-val">Aktif</span>
          <span class="stat-lbl">Status Sistem</span>
        </div>
        <span class="stat-link live-dot">Online</span>
      </div>
    </div>

    <!-- Stats Cards (Staff) -->
    <div v-else-if="user?.role === 'staff'" class="stats-row">
      <div class="stat-card" style="--c: #6366f1; --cb: #ede9fe;">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-val">{{ totalEnrollments }}</span>
          <span class="stat-lbl">Pelatihan Diikuti</span>
        </div>
        <router-link to="/admin/enrollments" class="stat-link">Lihat &rarr;</router-link>
      </div>

      <div class="stat-card" style="--c: #10b981; --cb: #d1fae5;">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-val">{{ recentEnrollments.filter(e => e.status === 'Lulus').length }}</span>
          <span class="stat-lbl">Pelatihan Lulus</span>
        </div>
      </div>

      <div class="stat-card" style="--c: #f59e0b; --cb: #fef3c7;">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-val">{{ recentEnrollments.filter(e => e.status === 'Enrolled').length }}</span>
          <span class="stat-lbl">Sedang Belajar</span>
        </div>
      </div>
    </div>

    <!-- Main content area -->
    <div class="main-grid">

      <!-- Left: Recent / Catalog Trainings -->
      <div class="section-card">
        <div class="section-head">
          <h3 class="section-title">
            {{ user?.role === 'admin' ? 'Pelatihan Terbaru' : 'Katalog Pelatihan' }}
          </h3>
          <router-link :to="user?.role === 'admin' ? '/admin/manage-trainings' : '/admin/trainings'"
                       class="see-all">Lihat Semua &rarr;</router-link>
        </div>

        <div v-if="loading" class="mini-loading">
          <div class="mini-spinner"></div>
        </div>

        <div v-else-if="trainings.length === 0" class="mini-empty">
          Belum ada pelatihan tersedia.
        </div>

        <div v-else class="training-list">
          <div v-for="t in trainings" :key="t.id" class="training-row">
            <div class="tr-num">{{ t.id }}</div>
            <div class="tr-info">
              <p class="tr-title">{{ t.title }}</p>
              <p class="tr-meta">KKM: {{ t.passing_grade }} poin</p>
            </div>
            <span :class="['tr-badge', t.status === 'Published' ? 'badge-pub' : 'badge-draft']">
              {{ t.status === 'Published' ? 'Live' : 'Draft' }}
            </span>
            <router-link
              :to="user?.role === 'admin' ? `/admin/manage-trainings/${t.id}` : `/admin/trainings/${t.id}`"
              class="tr-btn">
              &rarr;
            </router-link>
          </div>
        </div>
      </div>

      <!-- Right: Enrollments (Staff) or Quick Actions (Admin) -->
      <div class="section-card">
        <div v-if="user?.role === 'admin'">
          <div class="section-head"><h3 class="section-title">Aksi Cepat</h3></div>
          <div class="quick-actions">
            <router-link to="/admin/users" class="qa-item" style="--qa-c: #6366f1">
              <div class="qa-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
                  <line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/>
                </svg>
              </div>
              <div><p class="qa-title">Tambah Pengguna</p><p class="qa-sub">Kelola akun anggota</p></div>
            </router-link>

            <router-link to="/admin/manage-trainings" class="qa-item" style="--qa-c: #f59e0b">
              <div class="qa-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/>
                </svg>
              </div>
              <div><p class="qa-title">Kelola Pelatihan</p><p class="qa-sub">Materi & soal evaluasi</p></div>
            </router-link>

            <router-link to="/admin/trainings" class="qa-item" style="--qa-c: #10b981">
              <div class="qa-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/>
                </svg>
              </div>
              <div><p class="qa-title">Lihat Sebagai Peserta</p><p class="qa-sub">Tampilan katalog umum</p></div>
            </router-link>
          </div>
        </div>

        <div v-else>
          <div class="section-head">
            <h3 class="section-title">Progres Belajar</h3>
            <router-link to="/admin/enrollments" class="see-all">Semua &rarr;</router-link>
          </div>

          <div v-if="loading" class="mini-loading"><div class="mini-spinner"></div></div>

          <div v-else-if="recentEnrollments.length === 0" class="mini-empty">
            Anda belum mengikuti pelatihan apapun.
            <router-link to="/admin/trainings" class="mini-cta">Mulai Sekarang</router-link>
          </div>

          <div v-else class="enrollment-list">
            <div v-for="e in recentEnrollments" :key="e.id" class="enroll-row">
              <div class="er-top">
                <span :class="['er-badge',
                  e.status === 'Lulus' ? 'eb-lulus' :
                  e.status === 'Gagal' ? 'eb-gagal' : 'eb-proses']">
                  {{ e.status === 'Enrolled' ? 'Belajar' : e.status }}
                </span>
                <span class="er-date">{{ formatDate(e.enrolled_at) }}</span>
              </div>
              <div class="er-progress">
                <div class="er-bar-wrap">
                  <div class="er-bar"
                       :class="e.progress_percentage >= 100 ? 'bar-done' : 'bar-active'"
                       :style="`width: ${e.progress_percentage}%`"></div>
                </div>
                <span class="er-pct">{{ e.progress_percentage }}%</span>
              </div>
              <router-link :to="`/admin/trainings/${e.training_id}`" class="er-link">Lanjut Belajar &rarr;</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ── Hero Banner ─────────────────────────────────── */
.hero-banner {
  background: linear-gradient(135deg, var(--brown) 0%, #3d2314 60%, var(--maroon) 100%);
  border-radius: 24px;
  padding: 2.5rem 2.5rem;
  position: relative;
  overflow: hidden;
  color: white;
}
.hero-deco {
  position: absolute; border-radius: 50%;
  pointer-events: none;
}
.hero-deco-1 {
  width: 280px; height: 280px;
  background: rgba(255,255,255,0.05);
  top: -80px; right: -60px;
}
.hero-deco-2 {
  width: 180px; height: 180px;
  background: rgba(212, 172, 13, 0.15);
  bottom: -60px; left: 30%;
}
.hero-content {
  position: relative; z-index: 1;
  display: flex; justify-content: space-between; align-items: center; gap: 2rem;
}
.hero-text { flex: 1; }
.hero-date { font-size: 0.8rem; opacity: 0.7; margin-bottom: 0.5rem; letter-spacing: 0.05em; }
.hero-greeting {
  font-size: clamp(1.6rem, 3.5vw, 2.4rem);
  font-weight: 800; line-height: 1.2; margin: 0 0 0.75rem;
}
.hero-name { color: var(--gold); }
.hero-subtitle { font-size: 0.9rem; opacity: 0.8; margin-bottom: 1.5rem; line-height: 1.6; max-width: 480px; }
.hero-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.hero-btn {
  padding: 0.65rem 1.4rem; border-radius: 10px;
  font-size: 0.875rem; font-weight: 700;
  text-decoration: none; transition: all 0.2s;
  display: inline-block;
}
.hero-btn-primary {
  background: var(--gold); color: #1a0f00;
  box-shadow: 0 4px 12px rgba(212,172,13,0.4);
}
.hero-btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(212,172,13,0.5); }
.hero-btn-ghost {
  background: rgba(255,255,255,0.1);
  color: white; border: 1px solid rgba(255,255,255,0.2);
}
.hero-btn-ghost:hover { background: rgba(255,255,255,0.18); }
.hero-logo-wrap { flex-shrink: 0; }
.hero-logo { width: 120px; opacity: 0.85; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3)); }

@media (max-width: 640px) {
  .hero-logo-wrap { display: none; }
  .hero-banner { padding: 1.75rem 1.5rem; }
}

/* ── Stats Row ───────────────────────────────────── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
.stat-card {
  background: white;
  border-radius: 18px;
  padding: 1.25rem 1.5rem;
  border: 1px solid #f0ebe4;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  display: flex; align-items: center; gap: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
  animation: fadeUp 0.4s ease-out both;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.stat-icon {
  width: 48px; height: 48px; flex-shrink: 0;
  background: var(--cb); border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  color: var(--c);
}
.stat-icon svg { width: 22px; height: 22px; }
.stat-info { flex: 1; }
.stat-val { display: block; font-size: 1.75rem; font-weight: 800; color: #111827; line-height: 1.1; }
.stat-lbl { display: block; font-size: 0.75rem; color: #9ca3af; font-weight: 500; margin-top: 0.1rem; }
.stat-link {
  font-size: 0.75rem; font-weight: 600; color: var(--c);
  text-decoration: none; white-space: nowrap; flex-shrink: 0;
}
.stat-link:hover { text-decoration: underline; }
.live-dot { display: flex; align-items: center; gap: 0.3rem; }
.live-dot::before {
  content: '';
  display: inline-block; width: 7px; height: 7px;
  background: #10b981; border-radius: 50%;
  animation: pulse 2s infinite;
}

/* ── Main Grid ───────────────────────────────────── */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
@media (max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }

.section-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid #f0ebe4;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  animation: fadeUp 0.5s ease-out both;
}
.section-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 1.25rem;
}
.section-title { font-size: 1rem; font-weight: 700; color: #1f2937; margin: 0; }
.see-all { font-size: 0.8rem; font-weight: 600; color: var(--brown); text-decoration: none; }
.see-all:hover { color: var(--maroon); }

/* Training list */
.mini-loading { display: flex; justify-content: center; padding: 2rem; }
.mini-spinner {
  width: 32px; height: 32px;
  border: 3px solid #f3f4f6; border-top-color: var(--gold);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
.mini-empty { text-align: center; padding: 2rem 1rem; color: #9ca3af; font-size: 0.875rem; }
.mini-cta {
  display: block; margin-top: 0.75rem; color: var(--brown);
  font-weight: 600; text-decoration: none;
}
.mini-cta:hover { text-decoration: underline; }

.training-list { display: flex; flex-direction: column; gap: 0.6rem; }
.training-row {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.75rem; border-radius: 12px; border: 1px solid #f5f0eb;
  transition: background 0.18s;
}
.training-row:hover { background: #faf6f0; }
.tr-num {
  width: 32px; height: 32px; flex-shrink: 0;
  background: #f0ebe4; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; color: var(--brown);
}
.tr-info { flex: 1; min-width: 0; }
.tr-title { font-size: 0.875rem; font-weight: 600; color: #1f2937; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0; }
.tr-meta { font-size: 0.72rem; color: #9ca3af; margin: 0.1rem 0 0; }
.tr-badge { padding: 0.2rem 0.5rem; border-radius: 999px; font-size: 0.65rem; font-weight: 700; flex-shrink: 0; }
.badge-pub { background: #f0fdf4; color: #16a34a; }
.badge-draft { background: #fefce8; color: #ca8a04; }
.tr-btn {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; border-radius: 8px;
  background: var(--brown); color: white;
  font-size: 0.875rem; text-decoration: none;
  flex-shrink: 0; transition: background 0.2s;
}
.tr-btn:hover { background: var(--maroon); }

/* Quick Actions */
.quick-actions { display: flex; flex-direction: column; gap: 0.75rem; }
.qa-item {
  display: flex; align-items: center; gap: 1rem;
  padding: 1rem; border-radius: 14px;
  border: 1.5px solid transparent;
  background: #fafafa; text-decoration: none;
  transition: all 0.2s;
}
.qa-item:hover {
  border-color: var(--qa-c);
  background: white;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.qa-icon {
  width: 44px; height: 44px; flex-shrink: 0;
  background: color-mix(in srgb, var(--qa-c) 12%, white);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: var(--qa-c);
}
.qa-icon svg { width: 20px; height: 20px; }
.qa-title { font-size: 0.875rem; font-weight: 700; color: #1f2937; margin: 0; }
.qa-sub { font-size: 0.75rem; color: #9ca3af; margin: 0.1rem 0 0; }

/* Enrollment list */
.enrollment-list { display: flex; flex-direction: column; gap: 0.75rem; }
.enroll-row { padding: 0.875rem; border-radius: 12px; background: #fafafa; border: 1px solid #f0ebe4; }
.er-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; }
.er-badge { padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.65rem; font-weight: 700; }
.eb-lulus { background: #f0fdf4; color: #16a34a; }
.eb-gagal { background: #fef2f2; color: #dc2626; }
.eb-proses { background: #eff6ff; color: #2563eb; }
.er-date { font-size: 0.72rem; color: #9ca3af; }
.er-progress { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem; }
.er-bar-wrap { flex: 1; height: 7px; background: #e5e7eb; border-radius: 999px; overflow: hidden; }
.er-bar { height: 100%; border-radius: 999px; transition: width 0.8s ease; }
.bar-done { background: linear-gradient(90deg, #4ade80, #16a34a); }
.bar-active { background: linear-gradient(90deg, var(--gold), var(--brown)); }
.er-pct { font-size: 0.72rem; font-weight: 700; color: var(--brown); white-space: nowrap; }
.er-link { font-size: 0.775rem; font-weight: 600; color: var(--brown); text-decoration: none; }
.er-link:hover { color: var(--maroon); text-decoration: underline; }

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
