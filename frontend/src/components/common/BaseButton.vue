<script setup>
const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
})

const classes = {
  primary: 'bg-pramuka-600 text-white hover:bg-pramuka-700',
  secondary: 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50',
  danger: 'bg-red-600 text-white hover:bg-red-700',
  ghost: 'bg-transparent text-slate-600 hover:bg-slate-100'
}

const sizes = {
  sm: 'px-3 py-2 text-sm',
  md: 'px-4 py-2.5 text-sm',
  lg: 'px-5 py-3 text-base'
}
</script>

<template>
  <button
    :class="[`inline-flex items-center justify-center rounded-xl font-medium transition ${classes[variant] || classes.primary} ${sizes[size] || sizes.md}`, disabled || loading ? 'opacity-60 cursor-not-allowed' : '']"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white/50 border-t-white"></span>
    <slot />
  </button>
</template>
