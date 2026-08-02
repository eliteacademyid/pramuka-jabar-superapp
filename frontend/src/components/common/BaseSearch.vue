<script setup>
import { ref, watch } from 'vue'

const model = defineModel()
const props = defineProps({
  placeholder: { type: String, default: 'Cari...' },
  debounce: { type: Number, default: 300 }
})

const emit = defineEmits(['search'])
const localValue = ref(model.value || '')
let debounceTimer = null

watch(localValue, (val) => {
  model.value = val
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('search', val)
  }, props.debounce)
})

function clear() {
  localValue.value = ''
}
</script>

<template>
  <div class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2.5 shadow-sm focus-within:border-pramuka-500 focus-within:ring-2 focus-within:ring-pramuka-100">
    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 103.5 3.5a7.5 7.5 0 0013.15 13.15z" />
    </svg>
    <input
      v-model="localValue"
      :placeholder="placeholder"
      class="w-full bg-transparent text-sm outline-none"
    />
    <button
      v-if="localValue"
      class="flex-shrink-0 text-slate-400 hover:text-slate-600"
      @click="clear"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>
  </div>
</template>
