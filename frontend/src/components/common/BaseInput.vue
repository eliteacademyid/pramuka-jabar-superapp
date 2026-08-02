<script setup>
const model = defineModel()
const props = defineProps({
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  type: { type: String, default: 'text' },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  hint: { type: String, default: '' }
})
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm font-medium text-slate-700">
      {{ label }}
      <span v-if="required" class="ml-0.5 text-red-500">*</span>
    </label>
    <input
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :class="[
        'w-full rounded-xl border bg-white px-4 py-3 text-sm outline-none transition',
        error
          ? 'border-red-400 focus:border-red-500 focus:ring-2 focus:ring-red-100'
          : 'border-slate-200 focus:border-pramuka-500 focus:ring-2 focus:ring-pramuka-100',
        disabled ? 'cursor-not-allowed bg-slate-50 opacity-60' : ''
      ]"
    />
    <p v-if="hint && !error" class="text-xs text-slate-500">{{ hint }}</p>
    <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
  </div>
</template>
