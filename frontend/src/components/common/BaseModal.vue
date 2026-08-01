<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Modal' }
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 px-4">
    <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
      <div class="mb-4 flex items-start justify-between">
        <h3 class="text-lg font-semibold text-slate-800">{{ title }}</h3>
        <button class="text-slate-500 hover:text-slate-700" @click="close">✕</button>
      </div>
      <slot />
    </div>
  </div>
</template>
