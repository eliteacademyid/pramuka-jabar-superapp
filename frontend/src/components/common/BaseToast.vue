<script setup>
const props = defineProps({
  message: { type: String, default: '' },
  type: { type: String, default: 'success' }
})
</script>

<template>
  <div :class="[`rounded-xl border px-4 py-3 text-sm shadow-soft ${type === 'error' ? 'border-red-200 bg-red-50 text-red-700' : 'border-green-200 bg-green-50 text-green-700'}`]">
    {{ message }}
  </div>
</template>
