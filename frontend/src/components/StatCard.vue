<script setup>
defineProps({
  title: { type: String, default: '' },
  value: { type: [String, Number], default: '' },
  subtitle: { type: String, default: '' },
  icon: { type: Object, default: null },
  color: { type: String, default: 'text-pramuka-600' },
  bg: { type: String, default: 'bg-pramuka-50' },
  trend: { type: Number, default: null }
})
</script>

<template>
  <div class="flex items-start gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft transition hover:shadow-md">
    <div v-if="icon" :class="['flex-shrink-0 rounded-2xl p-3', bg, color]">
      <component :is="icon" class="h-6 w-6" />
    </div>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm text-slate-500">{{ title }}</p>
      <p class="mt-1 text-xl font-semibold text-slate-900">{{ value }}</p>
      <div v-if="subtitle || trend !== null" class="mt-1 flex items-center gap-1">
        <span v-if="trend !== null" :class="['text-xs font-medium', trend >= 0 ? 'text-green-600' : 'text-red-600']">
          {{ trend >= 0 ? '▲' : '▼' }} {{ Math.abs(trend) }}%
        </span>
        <span v-if="subtitle" class="text-xs text-slate-400">{{ subtitle }}</span>
      </div>
    </div>
  </div>
</template>
