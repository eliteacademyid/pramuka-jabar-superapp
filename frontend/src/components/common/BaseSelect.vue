<script setup>
const model = defineModel()
const props = defineProps({
  label: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Pilih opsi' }
})
</script>

<template>
  <label class="block text-sm font-medium text-slate-700">
    <span v-if="label" class="mb-2 block">{{ label }}</span>
    <select
      v-model="model"
      class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-pramuka-500 focus:ring-2 focus:ring-pramuka-100"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
