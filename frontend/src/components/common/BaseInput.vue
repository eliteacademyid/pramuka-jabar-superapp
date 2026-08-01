<script setup>
const model = defineModel()
const props = defineProps({
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  type: { type: String, default: 'text' },
  error: { type: String, default: '' }
})
</script>

<template>
  <label class="block text-sm font-medium text-slate-700">
    <span v-if="label" class="mb-2 block">{{ label }}</span>
    <input
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-pramuka-500 focus:ring-2 focus:ring-pramuka-100"
    />
    <p v-if="error" class="mt-2 text-sm text-red-600">{{ error }}</p>
  </label>
</template>
