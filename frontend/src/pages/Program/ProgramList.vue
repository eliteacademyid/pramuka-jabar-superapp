<template>
  <div class="space-y-6 p-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Daftar Program</h1>
        <p class="text-sm text-slate-500">Kelola data program kerja Kwarda Jawa Barat</p>
      </div>
    </div>

    <!-- Filter Card -->
    <div class="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft md:grid-cols-3">
      <ProgramSearch @search="onSearch" />
      <ProgramYearFilter @change="onYearChange" />
      <ProgramStatusFilter @change="onStatusChange" />
    </div>

    <!-- Program Table (Placeholder for now) -->
    <p class="text-gray-600">Table will appear here.</p>

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
import { ref } from 'vue'
import ProgramSearch from '@/components/ProgramSearch.vue'
import ProgramYearFilter from '@/components/ProgramYearFilter.vue'
import ProgramStatusFilter from '@/components/ProgramStatusFilter.vue'
import ProgramPagination from '@/components/ProgramPagination.vue'

const emit = defineEmits(['search', 'yearFilter', 'statusFilter', 'pageChange'])

const searchQuery = ref('')
const selectedYear = ref('')
const selectedStatus = ref('')

// Pagination state
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const perPage = ref(10)

function onSearch(value) {
  searchQuery.value = value
  emit('search', value)
}

function onYearChange(year) {
  selectedYear.value = year
  emit('yearFilter', year)
}

function onStatusChange(status) {
  selectedStatus.value = status
  emit('statusFilter', status)
}

function onPageChange(page) {
  currentPage.value = page
  emit('pageChange', page)
}
</script>

<style scoped>
/* No custom styles – rely on Tailwind */
</style>

