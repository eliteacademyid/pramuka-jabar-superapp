<template>
  <div class="space-y-6 p-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Daftar Program</h1>
        <p class="text-sm text-slate-500">Kelola data program kerja Kwarda Jawa Barat</p>
      </div>
    </div>

    <!-- Filter Card -->
    <div class="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft md:grid-cols-4">
      <ProgramSearch @search="onSearch" />
      <ProgramYearFilter @change="onYearChange" />
      <ProgramStatusFilter @change="onStatusChange" />
      <ProgramSorting @change="onSortChange" />
    </div>

    <!-- Program Table -->
    <ProgramTable
      :programs="programStore.programs"
      :loading="programStore.loading"
      @view="onView"
      @edit="onEdit"
      @delete="onDelete"
    />

    <!-- Program Pagination -->
    <ProgramPagination
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-items="totalItems"
      :per-page="perPage"
      @change="onPageChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProgramStore } from '@/store/program'
import ProgramSearch from '@/components/ProgramSearch.vue'
import ProgramYearFilter from '@/components/ProgramYearFilter.vue'
import ProgramStatusFilter from '@/components/ProgramStatusFilter.vue'
import ProgramSorting from '@/components/ProgramSorting.vue'
import ProgramPagination from '@/components/ProgramPagination.vue'
import ProgramTable from '@/components/ProgramTable.vue'

const router = useRouter()
const programStore = useProgramStore()

const searchQuery = ref('')
const selectedYear = ref('')
const selectedStatus = ref('')
const sortBy = ref('created_at')
const sortDir = ref('desc')

// Pagination state
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const perPage = ref(10)

async function loadPrograms() {
  const params = {
    skip: (currentPage.value - 1) * perPage.value,
    limit: perPage.value,
    search: searchQuery.value || undefined,
    tahun: selectedYear.value ? Number(selectedYear.value) : undefined,
    status: selectedStatus.value || undefined,
    sort_by: sortBy.value,
    order: sortDir.value
  }
  try {
    const data = await programStore.fetchPrograms(params)
    // Simple pagination estimation
    if (data.length === perPage.value) {
      totalPages.value = currentPage.value + 1
    } else {
      totalPages.value = currentPage.value
    }
    totalItems.value = (currentPage.value - 1) * perPage.value + data.length
  } catch (err) {
    console.error('Error loading programs:', err)
  }
}

onMounted(() => {
  loadPrograms()
})

function onSearch(value) {
  searchQuery.value = value
  currentPage.value = 1
  loadPrograms()
}

function onYearChange(year) {
  selectedYear.value = year
  currentPage.value = 1
  loadPrograms()
}

function onStatusChange(status) {
  selectedStatus.value = status
  currentPage.value = 1
  loadPrograms()
}

function onSortChange({ order_by, order_dir }) {
  sortBy.value = order_by
  sortDir.value = order_dir
  currentPage.value = 1
  loadPrograms()
}

function onPageChange(page) {
  currentPage.value = page
  loadPrograms()
}

function onView(id) {
  router.push({ name: 'program-detail', params: { id } })
}

function onEdit(id) {
  router.push({ name: 'program-edit', params: { id } })
}

function onDelete(id) {
  console.log('Delete program:', id)
}
</script>

<style scoped>
/* No custom styles – rely on Tailwind */
</style>

