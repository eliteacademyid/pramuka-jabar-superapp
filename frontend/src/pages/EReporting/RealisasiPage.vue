<script setup>
import { onMounted, ref, computed } from 'vue'
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
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ArrowPathIcon,
  PaperClipIcon
} from '@heroicons/vue/24/outline'

const store = useEReportingStore()

// ─── Filter & search ───────────────────────────────────────────
const search = ref('')
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
  if (search.value) params.search = search.value
  if (filterStatus.value) params.status = filterStatus.value
  await store.fetchRealisasi(params)
}

onMounted(loadData)

// ─── Form create ──────────────────────────────────────────────
const showModal = ref(false)
const saving = ref(false)
const formError = ref('')
const toast = ref(null)

const form = ref({
  judul: '',
  deskripsi: '',
  target: '',
  realisasi: '',
  periode: '',
  status: 'draft',
  program_id: '',
  kegiatan_id: ''
})

const formStatusOptions = [
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' }
]

// Upload file
const fileInput = ref(null)
const uploadedFile = ref(null)
const uploading = ref(false)

async function handleFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  try {
    const result = await store.uploadFile(file)
    uploadedFile.value = result
    showToast('File berhasil diupload', 'success')
  } catch (err) {
    showToast(err.response?.data?.detail || 'Upload file gagal', 'error')
  } finally {
    uploading.value = false
  }
}

function openCreate() {
  form.value = { judul: '', deskripsi: '', target: '', realisasi: '', periode: '', status: 'draft', program_id: '', kegiatan_id: '' }
  uploadedFile.value = null
  formError.value = ''
  showModal.value = true
}

async function submitForm() {
  if (!form.value.judul.trim()) {
    formError.value = 'Judul realisasi tidak boleh kosong'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    const payload = {
      judul: form.value.judul.trim(),
      deskripsi: form.value.deskripsi || null,
      target: form.value.target ? Number(form.value.target) : null,
      realisasi: form.value.realisasi ? Number(form.value.realisasi) : null,
      periode: form.value.periode || null,
      status: form.value.status,
      program_id: form.value.program_id ? Number(form.value.program_id) : null,
      kegiatan_id: form.value.kegiatan_id ? Number(form.value.kegiatan_id) : null
    }
    await store.createRealisasi(payload)
    showModal.value = false
    showToast('Realisasi berhasil dibuat')
    await loadData()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan realisasi'
  } finally {
    saving.value = false
  }
}

// ─── Badge status ─────────────────────────────────────────────
function statusVariant(s) {
  return { draft: 'default', submitted: 'info', approved: 'success', rejected: 'danger' }[s] ?? 'default'
}

function statusLabel(s) {
  return { draft: 'Draft', submitted: 'Submitted', approved: 'Disetujui', rejected: 'Ditolak' }[s] ?? s
}

// ─── Persentase capaian ───────────────────────────────────────
function persen(item) {
  if (!item.target || item.target === 0) return '-'
  return Math.round((item.realisasi / item.target) * 100) + '%'
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
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">Realisasi Program & Kegiatan</h2>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">
          Catat dan pantau realisasi pelaksanaan program dan kegiatan Pramuka Jawa Barat.
        </p>
      </div>
      <BaseButton @click="openCreate">
        <PlusIcon class="mr-2 h-4 w-4" />
        Tambah Realisasi
      </BaseButton>
    </div>

    <!-- Toast -->
    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 -translate-y-2" leave-active-class="transition duration-200 ease-in" leave-to-class="opacity-0 -translate-y-2">
      <BaseToast v-if="toast" :message="toast.message" :type="toast.type" />
    </Transition>

    <!-- Filter bar -->
    <BaseCard>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end">
        <div class="relative flex-1">
          <MagnifyingGlassIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            v-model="search"
            type="text"
            placeholder="Cari judul realisasi..."
            class="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-pramuka-500 focus:ring-2 focus:ring-pramuka-100"
            @input="loadData"
          />
        </div>
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
    <div v-if="store.realisasiLoading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <BaseLoading v-for="i in 6" :key="i" />
    </div>

    <!-- Empty state -->
    <div v-else-if="store.realisasiList.length === 0" class="flex flex-col items-center justify-center rounded-[28px] border border-dashed border-slate-200 bg-white py-20 text-center">
      <DocumentTextIcon class="h-12 w-12 text-slate-300" />
      <p class="mt-4 text-sm font-medium text-slate-500">Belum ada data realisasi</p>
      <p class="mt-1 text-xs text-slate-400">Klik "Tambah Realisasi" untuk mulai mencatat</p>
    </div>

    <!-- Tabel realisasi -->
    <BaseCard v-else title="Daftar Realisasi" :subtitle="`${store.realisasiList.length} data ditemukan`">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-100">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Judul</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Periode</th>
              <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Target</th>
              <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Realisasi</th>
              <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Capaian</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Dokumen</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            <tr v-for="item in store.realisasiList" :key="item.id" class="hover:bg-slate-50/60 transition">
              <td class="px-4 py-3">
                <p class="text-sm font-medium text-slate-800">{{ item.judul }}</p>
                <p v-if="item.deskripsi" class="mt-0.5 max-w-xs truncate text-xs text-slate-400">{{ item.deskripsi }}</p>
              </td>
              <td class="px-4 py-3 text-sm text-slate-600">{{ item.periode || '-' }}</td>
              <td class="px-4 py-3 text-right text-sm text-slate-700">{{ item.target ?? '-' }}</td>
              <td class="px-4 py-3 text-right text-sm text-slate-700">{{ item.realisasi ?? '-' }}</td>
              <td class="px-4 py-3 text-right">
                <span
                  :class="[
                    'text-sm font-semibold',
                    item.target && item.realisasi >= item.target ? 'text-green-600' : 'text-amber-600'
                  ]"
                >
                  {{ persen(item) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <BaseBadge :variant="statusVariant(item.status)">{{ statusLabel(item.status) }}</BaseBadge>
              </td>
              <td class="px-4 py-3">
                <span v-if="item.documents && item.documents.length > 0" class="inline-flex items-center gap-1 text-xs text-pramuka-600">
                  <PaperClipIcon class="h-3.5 w-3.5" />
                  {{ item.documents.length }} file
                </span>
                <span v-else class="text-xs text-slate-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <!-- Modal Tambah Realisasi -->
    <BaseModal v-model="showModal" title="Tambah Realisasi">
      <form class="space-y-4" @submit.prevent="submitForm">
        <div v-if="formError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ formError }}
        </div>

        <BaseInput v-model="form.judul" label="Judul Realisasi *" placeholder="Masukkan judul realisasi" />

        <BaseTextarea v-model="form.deskripsi" label="Deskripsi" placeholder="Deskripsi realisasi (opsional)" />

        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.target" type="number" label="Target" placeholder="0" />
          <BaseInput v-model="form.realisasi" type="number" label="Realisasi" placeholder="0" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.periode" label="Periode" placeholder="Contoh: Q1 2026" />
          <BaseSelect v-model="form.status" label="Status" :options="formStatusOptions" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <BaseInput v-model="form.program_id" type="number" label="Program ID (opsional)" placeholder="ID program" />
          <BaseInput v-model="form.kegiatan_id" type="number" label="Kegiatan ID (opsional)" placeholder="ID kegiatan" />
        </div>

        <!-- Upload file -->
        <div>
          <p class="mb-2 block text-sm font-medium text-slate-700">Lampiran Dokumen (opsional)</p>
          <label class="flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-500 transition hover:border-pramuka-400 hover:bg-pramuka-50">
            <PaperClipIcon class="h-5 w-5 text-pramuka-500" />
            <span>{{ uploading ? 'Mengupload...' : uploadedFile ? uploadedFile.filename : 'Pilih file untuk diupload' }}</span>
            <input ref="fileInput" type="file" class="hidden" :disabled="uploading" @change="handleFileChange" />
          </label>
          <p v-if="uploadedFile" class="mt-1 text-xs text-green-600">✓ {{ uploadedFile.message }}</p>
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <BaseButton type="button" variant="secondary" @click="showModal = false">Batal</BaseButton>
          <BaseButton type="submit" :loading="saving">Simpan Realisasi</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
