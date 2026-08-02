<script setup>
const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  totalItems: { type: Number, default: 0 },
  perPage: { type: Number, default: 10 }
})

const emit = defineEmits(['change'])

function goTo(page) {
  if (page >= 1 && page <= props.totalPages) {
    emit('change', page)
  }
}

function getPages() {
  const range = []
  const delta = 2
  for (let i = Math.max(1, props.currentPage - delta); i <= Math.min(props.totalPages, props.currentPage + delta); i++) {
    range.push(i)
  }
  return range
}
</script>

<template>
  <div class="mt-4 flex flex-col items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 sm:flex-row">
    <span class="text-slate-500">
      Menampilkan {{ Math.min((currentPage - 1) * perPage + 1, totalItems) }}–{{ Math.min(currentPage * perPage, totalItems) }} dari {{ totalItems }} data
    </span>
    <div class="flex items-center gap-1">
      <button
        class="rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="currentPage <= 1"
        @click="goTo(currentPage - 1)"
      >
        Sebelumnya
      </button>
      <button
        v-for="page in getPages()"
        :key="page"
        :class="[
          'rounded-lg border px-3 py-2 text-xs font-medium transition',
          page === currentPage
            ? 'border-pramuka-600 bg-pramuka-600 text-white'
            : 'border-slate-200 hover:bg-slate-50'
        ]"
        @click="goTo(page)"
      >
        {{ page }}
      </button>
      <button
        class="rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="currentPage >= totalPages"
        @click="goTo(currentPage + 1)"
      >
        Berikutnya
      </button>
    </div>
  </div>
</template>
