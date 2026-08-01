<script setup>
const model = defineModel()
const props = defineProps({
  placeholder: { type: String, default: 'Cari...' }
})
</script>

<template>
  <div class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 103.5 3.5a7.5 7.5 0 0013.15 13.15z" />
    </svg>
    <input v-model="model" :placeholder="placeholder" class="w-full bg-transparent text-sm outline-none" />
  </div>
</template>
