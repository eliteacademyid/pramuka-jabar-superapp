<script setup>
const props = defineProps({
  variant: { type: String, default: 'default' },
  size: { type: String, default: 'md' }
})

const variants = {
  default: 'bg-slate-100 text-slate-700',
  success: 'bg-green-100 text-green-700',
  warning: 'bg-amber-100 text-amber-700',
  danger: 'bg-red-100 text-red-700',
  info: 'bg-blue-100 text-blue-700',
  purple: 'bg-purple-100 text-purple-700',
  pramuka: 'bg-pramuka-100 text-pramuka-700'
}

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-xs',
  lg: 'px-4 py-1.5 text-sm'
}
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1 rounded-full font-semibold',
      variants[variant] || variants.default,
      sizes[size] || sizes.md
    ]"
  >
    <slot />
  </span>
</template>
