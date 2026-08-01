<script setup>
import { onMounted, ref, computed } from 'vue'
import { useEReportingStore } from '../../store/ereporting'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseButton from '../../components/common/BaseButton.vue'
import BaseModal from '../../components/common/BaseModal.vue'
import BaseTextarea from '../../components/common/BaseTextarea.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseToast from '../../components/common/BaseToast.vue'
import {
  ArrowPathIcon,
  ClipboardDocumentCheckIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

const store = useEReportingStore()

// ─── Load laporan yang bisa di-approve (submitted / draft) ────
const filterStatus = ref('submitted')
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

// ─── Ringkasan ────────────────────────────────────────────────
const totalSubmitted = computed(() =>
  store.laporanList.filter((l) => l.status === 'submitted').length
)
const totalApproved = computed(() =>
  store.laporanList.filter((l) => l.status === 'approved').length
)
const totalRejected = computed(() =>
  store.laporanList.filter((l) => l.status === 'rejected').length
)

// ─── Modal approve / reject ───────────────────────────────────
const showModal = ref(false)
const modalMode = ref('approved') // 'approved' | 'rejected'
const selectedLaporan = ref(null)
const catatan = ref('')
const processing = ref(false)
const formError = ref('')
const toast = ref(null)

function openApprove(laporan) {
  selectedLaporan.value = laporan
  modalMode.value = 'approved'
  catatan.value = ''
  formError.value = ''
  showModal.value = true
}

function openReject(laporan) {
  selectedLaporan.value = laporan
  modalMode.value = 'rejected'
  catatan.value = ''
  formError.value = ''
  showModal.value = true
}

async function submitApproval() {
  if (!selectedLaporan.value) return
  processing.value = true
  formError.value = ''
  try {
    // Payload sesuai ApprovalCreate backend:
    // { laporan_id: int, status: 'approved'|'rejected', catatan?: str }
    await store.processApproval({
      laporan_id: selectedLaporan.value.id,
      status: modalMode.value,
      catatan: catatan.value.trim() || null
    })
    showModal.value = false
    showToast(
      modalMode.value === 'approved'
        ? `Laporan "${selectedLaporan.value.judul}" berhasil disetujui`
        : `Laporan "${selectedLaporan.value.judul}" ditolak`,
      modalMode.value === 'approved' ? 'success' : 'error'
    )
    await loadData()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal memproses approval'
  } finally {
    processing.value = false
  }
}

// ─── Badge & format ───────────────────────────────────────────
function statusVariant(s) {
  return { draft: 'default', submitted: 'info', approved: 'success', rejected: 'danger' }[s] ?? 'default'
}

function statusLabel(s) {
  return { draft: 'Draft', submitted: 'Menunggu Review', approved: 'Disetujui', rejected: 'Ditolak' }[s] ?? s
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

// Laporan yang sudah approved/rejected tidak bisa diubah lagi (sesuai backend)
function canProcess(laporan) {
  return laporan.status !== 'approved' && laporan.status !== 'rejected'
}

// ─── Toast ────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  toast.value = { message, type }
  setTimeout(() => (toast.value = null), 4000)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-pramuka-600">Modul 3 · E-Reporting</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">Approval Laporan</h2>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Tinjau dan proses approval laporan yang telah disubmit. Laporan yang sudah disetujui tidak dapat diubah kembali.
        </p>
      </div>
      <BaseBadge variant="info">
        <ShieldCheckIcon class="mr-1.5 h-3.5 w-3.5" />
        Hak Akses Reviewer
      </BaseBadge>
    </div>

    <!-- Toast -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      leave-active-class="transition duration-200 ease-in"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <BaseToast v-if="toast" :message="toast.message" :type="toast.type" />
    </Transition>

    <!-- Stat cards -->
    <div v-if="!store.laporanLoading" class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-blue-50 p-3">
          <ClockIcon class="h-5 w-5 text-blue-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Menunggu Review</p>
          <p class="text-2xl font-bold text-blue-600">{{ totalSubmitted }}</p>
        </div>
      </BaseCard>
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-green-50 p-3">
          <CheckCircleIcon class="h-5 w-5 text-green-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Disetujui</p>
          <p class="text-2xl font-bold text-green-600">{{ totalApproved }}</p>
        </div>
      </BaseCard>
      <BaseCard class="flex items-center gap-4">
        <div class="rounded-2xl bg-red-50 p-3">
          <XCircleIcon class="h-5 w-5 text-red-500" />
        </div>
        <div>
          <p class="text-xs text-slate-500">Ditolak</p>
          <p class="text-2xl font-bold text-red-600">{{ totalRejected }}</p>
        </div>
      </BaseCard>
    </div>

    <!-- Filter -->
    <BaseCard>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div class="w-full sm:w-60">
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
      <ClipboardDocumentCheckIcon class="h-12 w-12 text-slate-300" />
      <p class="mt-4 text-sm font-medium text-slate-500">Tidak ada laporan untuk ditinjau</p>
      <p class="mt-1 text-xs text-slate-400">Laporan yang disubmit akan muncul di sini</p>
    </div>

    <!-- Tabel laporan -->
    <BaseCard v-else title="Daftar Laporan untuk Ditinjau" :subtitle="`${store.laporanList.length} laporan`">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-100">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Laporan</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Periode</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Dibuat</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Realisasi</th>
              <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="item in store.laporanList" :key="item.id" class="transition hover:bg-slate-50/60">
              <td class="px-4 py-3">
                <p class="text-sm font-medium text-slate-800">{{ item.judul }}</p>
                <p v-if="item.deskripsi" class="mt-0.5 max-w-xs truncate text-xs text-slate-400">{{ item.deskripsi }}</p>
                <p class="mt-0.5 text-xs text-slate-400">ID #{{ item.id }} · Oleh User #{{ item.created_by_id }}</p>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ item.periode || '-' }}</td>
              <td class="px-4 py-3">
                <BaseBadge :variant="statusVariant(item.status)">{{ statusLabel(item.status) }}</BaseBadge>
              </td>
              <td class="px-4 py-3 text-sm text-slate-500">{{ formatDate(item.created_at) }}</td>
              <td class="px-4 py-3 text-sm text-slate-600">
                <span v-if="item.realisasi_id" class="rounded-lg bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                  #{{ item.realisasi_id }}
                </span>
                <span v-else class="text-slate-400">-</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-2">
                  <template v-if="canProcess(item)">
                    <BaseButton size="sm" @click="openApprove(item)">
                      <CheckCircleIcon class="mr-1 h-3.5 w-3.5" />
                      Setujui
                    </BaseButton>
                    <BaseButton size="sm" variant="danger" @click="openReject(item)">
                      <XCircleIcon class="mr-1 h-3.5 w-3.5" />
                      Tolak
                    </BaseButton>
                  </template>
                  <span v-else class="text-xs text-slate-400 italic">Sudah diproses</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- Modal Konfirmasi Approve / Reject -->
    <BaseModal
      v-model="showModal"
      :title="modalMode === 'approved' ? 'Setujui Laporan' : 'Tolak Laporan'"
    >
      <div class="space-y-4">
        <!-- Info laporan yang dipilih -->
        <div
          :class="[
            'rounded-xl border p-4',
            modalMode === 'approved'
              ? 'border-green-200 bg-green-50'
              : 'border-red-200 bg-red-50'
          ]"
        >
          <div class="flex items-start gap-3">
            <component
              :is="modalMode === 'approved' ? CheckCircleIcon : XCircleIcon"
              :class="['h-5 w-5 mt-0.5', modalMode === 'approved' ? 'text-green-600' : 'text-red-600']"
            />
            <div>
              <p :class="['text-sm font-semibold', modalMode === 'approved' ? 'text-green-800' : 'text-red-800']">
                {{ selectedLaporan?.judul }}
              </p>
              <p :class="['mt-0.5 text-xs', modalMode === 'approved' ? 'text-green-600' : 'text-red-600']">
                {{ modalMode === 'approved'
                  ? 'Laporan ini akan ditandai sebagai Disetujui dan tidak dapat diubah kembali.'
                  : 'Laporan ini akan ditolak. Pembuat laporan perlu merevisi dan submit ulang.' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="formError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ formError }}
        </div>

        <!-- Catatan -->
        <BaseTextarea
          v-model="catatan"
          :label="modalMode === 'approved' ? 'Catatan (opsional)' : 'Alasan Penolakan (opsional)'"
          :placeholder="modalMode === 'approved' ? 'Tambahkan catatan approval...' : 'Jelaskan alasan penolakan...'"
        />

        <div class="flex justify-end gap-3 pt-1">
          <BaseButton type="button" variant="secondary" @click="showModal = false">Batal</BaseButton>
          <BaseButton
            :variant="modalMode === 'approved' ? 'primary' : 'danger'"
            :loading="processing"
            @click="submitApproval"
          >
            <component :is="modalMode === 'approved' ? CheckCircleIcon : XCircleIcon" class="mr-1.5 h-4 w-4" />
            {{ modalMode === 'approved' ? 'Ya, Setujui' : 'Ya, Tolak' }}
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>
