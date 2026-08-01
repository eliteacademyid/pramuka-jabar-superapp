<script setup>
const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' }
})
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
    <div v-if="title || subtitle" class="mb-4">
      <h3 class="text-lg font-semibold text-slate-800">{{ title }}</h3>
      <p v-if="subtitle" class="text-sm text-slate-500">{{ subtitle }}</p>
    </div>
    <slot />
  </section>
</template>
