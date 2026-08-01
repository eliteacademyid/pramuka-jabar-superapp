<script setup>
const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 }
})

const emit = defineEmits(['change'])
</script>

<template>
  <div class="mt-4 flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
    <span>Halaman {{ currentPage }} dari {{ totalPages }}</span>
    <div class="flex items-center gap-2">
      <button class="rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50" @click="emit('change', currentPage - 1)">Sebelumnya</button>
      <button class="rounded-lg border border-slate-200 px-3 py-2 hover:bg-slate-50" @click="emit('change', currentPage + 1)">Berikutnya</button>
    </div>
  </div>
</template>
