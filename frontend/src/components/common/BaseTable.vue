<script setup>
const props = defineProps({
  headers: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] }
})
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
    <table class="min-w-full divide-y divide-slate-200">
      <thead class="bg-slate-50">
        <tr>
          <th v-for="header in headers" :key="header" class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">
            {{ header }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <tr v-for="(row, index) in rows" :key="index" class="hover:bg-slate-50">
          <td v-for="(value, key) in row" :key="key" class="px-4 py-3 text-sm text-slate-700">
            {{ value }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
