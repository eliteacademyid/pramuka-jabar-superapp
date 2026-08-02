<script setup>
const model = defineModel()
const props = defineProps({
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  rows: { type: Number, default: 4 },
  error: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  maxlength: { type: Number, default: null },
  required: { type: Boolean, default: false }
})
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" class="text-sm font-medium text-slate-700">
      {{ label }}
      <span v-if="required" class="ml-0.5 text-red-500">*</span>
    </label>
    <textarea
      v-model="model"
      :rows="rows"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxlength"
      :required="required"
      :class="[
        'w-full resize-y rounded-xl border bg-white px-4 py-3 text-sm outline-none transition',
        error
          ? 'border-red-400 focus:border-red-500 focus:ring-2 focus:ring-red-100'
          : 'border-slate-200 focus:border-pramuka-500 focus:ring-2 focus:ring-pramuka-100',
        disabled ? 'cursor-not-allowed opacity-60' : ''
      ]"
    />
    <div class="flex items-center justify-between">
      <p v-if="error" class="text-xs text-red-600">{{ error }}</p>
      <p v-if="maxlength" class="ml-auto text-xs text-slate-400">{{ model?.length ?? 0 }}/{{ maxlength }}</p>
    </div>
  </div>
</template>
