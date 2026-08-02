<script setup>
const props = defineProps({
  text: { type: String, default: 'Memuat data...' },
  fullscreen: { type: Boolean, default: false }
})
</script>

<template>
  <div
    :class="[
      'flex items-center justify-center',
      fullscreen
        ? 'fixed inset-0 z-50 bg-white/80 backdrop-blur'
        : 'rounded-2xl border border-slate-200 bg-white p-10 shadow-soft'
    ]"
  >
    <div class="flex flex-col items-center gap-3 text-slate-600">
      <div class="relative h-12 w-12">
        <div class="absolute inset-0 animate-spin rounded-full border-4 border-pramuka-100 border-t-pramuka-600"></div>
        <div class="absolute inset-2 animate-ping rounded-full bg-pramuka-100 opacity-50"></div>
      </div>
      <p class="text-sm font-medium">{{ text }}</p>
    </div>
  </div>
</template>
