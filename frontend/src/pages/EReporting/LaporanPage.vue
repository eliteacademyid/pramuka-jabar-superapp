<script setup>
import { onMounted, ref } from 'vue'
import { useEReportingStore } from '../../store/ereporting'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseButton from '../../components/common/BaseButton.vue'
import BaseModal from '../../components/common/BaseModal.vue'
import BaseInput from '../../components/common/BaseInput.vue'
import BaseSelect from '../../components/common/BaseSelect.vue'
import BaseTextarea from '../../components/common/BaseTextarea.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseToast from '../../components/common/BaseToast.vue'
import {
  PlusIcon,
  ArrowPathIcon,
  DocumentChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

const store = useEReportingStore()

// ─── Filter ───────────────────────────────────────────────────
const filterStatus = ref('')
const statusOptions = [
  { value: '', label: 'Semua Status' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' }
]

async function loadData() {
  const params = {}
  if (filterStatus.value) params.status = filterStatus.value
  await store.fetchLaporan(params)
}

onMounted(loadData)

// ─── Ringkasan status ─────────────────────────────────────────
function countByStatus(s) {
  return store.laporanList.filter((l) => l.status === s).length
}

// ─── Form create ──────────────────────────────────────────────
const showModal = ref(false)
const saving = ref(false)
const formError = ref('')
const toast = ref(null)

const form = ref({
  judul: '',
  periode: '',
  deskripsi: '',
  status: 'draft',
  realisasi_id: ''
})

const formStatusOptions = [
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' }
]

function openCreate() {
  form.value = { judul: '', periode: '', deskripsi: '', status: 'draft', realisasi_id: '' }
  formError.value = ''
  showModal.value = true
}

async function submitForm() {
  if (!form.value.judul.trim()) {
    formError.value = 'Judul laporan tidak boleh kosong'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      judul: form.value.judul.trim(),
      periode: form.value.periode || null,
      deskripsi: form.value.deskripsi || null,
      status: form.value.status,
      realisasi_id: form.value.realisasi_id ? Number(form.value.realisasi_id) : null
    }
    await store.createLaporan(payload)
    showModal.value = false
    showToast('Laporan berhasil dibuat')
    await loadData()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan laporan'
  } finally {
    saving.value = false
  }
}

// ─── Badge & format ───────────────────────────────────────────
function statusVariant(s) {
  return { draft: 'default', submitted: 'info', approved: 'success', rejected: 'danger' }[s] ?? 'default'
}

function statusLabel(s) {
  return { draft: 'Draft', submitted: 'Submitted', approved: 'Disetujui', rejected: 'Ditolak' }[s] ?? s
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

// ─── Toast ────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  toast.value = { message, type }
  setTimeout(() => (toast.value = null), 3500)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-pramuka-600">Modul 3 · E-Reporting</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">Laporan Pelaksanaan</h2>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Unggah dan kelola laporan hasil pelaksanaan kegiatan. Laporan yang sudah disubmit dapat diajukan ke proses approval.
        </p>
      </div>
      <BaseButton @click="openCreate">
        <PlusIcon class="mr-2 h-4 w-4" />
        Buat Laporan
      </BaseButton>
    </div>

    <!-- Toast -->
    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2" leave-active-class="transition duration-200 ease-in" leave-to-class="opacity-0 -translate-y-2">
      <BaseToast v-if="toast" :message="toast.message" :type="toast.type" />
    </Transition>

    <!-- Stat cards ringkasan -->
    <div v-if="!store.laporanLoading" class="grid grid-cols-2 gap-4 lg:grid-cols-4">
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-slate-100 p-3">
          <DocumentChartBarIcon class="h-5 w-5 text-slate-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Total Laporan</p>
          <p class="text-xl font-semibold text-slate-900">{{ store.laporanList.length }}</p>
        </div>
      </BaseCard>
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-amber-50 p-3">
          <ClockIcon class="h-5 w-5 text-amber-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Pending</p>
          <p class="text-xl font-semibold text-amber-600">{{ countByStatus('draft') + countByStatus('submitted') }}</p>
        </div>
      </BaseCard>
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-green-50 p-3">
          <CheckCircleIcon class="h-5 w-5 text-green-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Disetujui</p>
          <p class="text-xl font-semibold text-green-600">{{ countByStatus('approved') }}</p>
        </div>
      </BaseCard>
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-red-50 p-3">
          <XCircleIcon class="h-5 w-5 text-red-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Ditolak</p>
          <p class="text-xl font-semibold text-red-600">{{ countByStatus('rejected') }}</p>
        </div>
      </BaseCard>
    </div>

    <!-- Filter bar -->
    <BaseCard>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div class="w-full sm:w-52">
          <select
            v-model="filterStatus"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-pramuka-500 focus:ring-2 focus:ring-pramuka-100"
            @change="loadData"
          >
            <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>
        <BaseButton variant="secondary" @click="loadData">
          <ArrowPathIcon class="h-4 w-4" />
        </BaseButton>
      </div>
    </BaseCard>

    <!-- Loading -->
    <div v-if="store.laporanLoading" class="grid gap-4 md:grid-cols-2">
      <BaseLoading v-for="i in 4" :key="i" />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="store.laporanList.length === 0"
      class="flex flex-col items-center justify-center rounded-[28px] border border-dashed border-slate-200 bg-white py-20 text-center"
    >
      <DocumentChartBarIcon class="h-12 w-12 text-slate-300" />
      <p class="mt-4 text-sm font-medium text-slate-500">Belum ada laporan</p>
      <p class="mt-1 text-xs text-slate-400">Klik "Buat Laporan" untuk mulai membuat laporan</p>
    </div>

    <!-- Tabel laporan -->
    <BaseCard v-else title="Daftar Laporan" :subtitle="`${store.laporanList.length} laporan ditemukan`">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-100">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Judul</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Periode</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Realisasi ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Dibuat</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Disetujui Oleh</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="item in store.laporanList" :key="item.id" class="transition hover:bg-slate-50/60">
              <td class="px-4 py-3">
                <p class="text-sm font-medium text-slate-800">{{ item.judul }}</p>
                <p v-if="item.deskripsi" class="mt-0.5 max-w-xs truncate text-xs text-slate-400">{{ item.deskripsi }}</p>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ item.periode || '-' }}</td>
              <td class="px-4 py-3">
                <BaseBadge :variant="statusVariant(item.status)">{{ statusLabel(item.status) }}</BaseBadge>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">
                <span v-if="item.realisasi_id" class="rounded-lg bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                  #{{ item.realisasi_id }}
                </span>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="px-4 py-3 text-sm text-slate-500">{{ formatDate(item.created_at) }}</td>
              <td class="px-4 py-3 text-sm text-slate-500">
                <span v-if="item.approved_by_id" class="inline-flex items-center gap-1 text-green-600">
                  <CheckCircleIcon class="h-3.5 w-3.5" />
                  User #{{ item.approved_by_id }}
                </span>
                <span v-else class="text-slate-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- Modal Buat Laporan -->
    <BaseModal v-model="showModal" title="Buat Laporan Baru">
      <form class="space-y-4" @submit.prevent="submitForm">
        <div v-if="formError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ formError }}
        </div>

        <BaseInput v-model="form.judul" label="Judul Laporan *" placeholder="Masukkan judul laporan" />

        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.periode" label="Periode" placeholder="Contoh: Q1 2026" />
          <BaseSelect v-model="form.status" label="Status Awal" :options="formStatusOptions" />
        </div>

        <BaseTextarea v-model="form.deskripsi" label="Deskripsi" placeholder="Deskripsi laporan (opsional)" />

        <BaseInput
          v-model="form.realisasi_id"
          type="number"
          label="Referensi Realisasi ID (opsional)"
          placeholder="Masukkan ID realisasi yang terkait"
        />

        <div class="flex justify-end gap-3 pt-2">
          <BaseButton type="button" variant="secondary" @click="showModal = false">Batal</BaseButton>
          <BaseButton type="submit" :loading="saving">Simpan Laporan</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
