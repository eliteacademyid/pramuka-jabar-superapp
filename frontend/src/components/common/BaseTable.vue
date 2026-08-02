<script setup>
const props = defineProps({
  headers: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Tidak ada data yang ditampilkan.' }
})
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr>
            <th
              v-for="header in headers"
              :key="header"
              class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600"
            >
              {{ header }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <template v-if="loading">
            <tr v-for="n in 3" :key="n">
              <td v-for="header in headers" :key="header" class="px-4 py-3">
                <div class="h-4 w-full animate-pulse rounded-lg bg-slate-200"></div>
              </td>
            </tr>
          </template>
          <template v-else-if="rows.length === 0">
            <tr>
              <td :colspan="headers.length" class="px-4 py-8 text-center text-sm text-slate-400">
                {{ emptyText }}
              </td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="(row, index) in rows" :key="index" class="hover:bg-slate-50">
              <slot :row="row" :index="index">
                <td v-for="(value, key) in row" :key="key" class="px-4 py-3 text-sm text-slate-700">
                  {{ value }}
                </td>
              </slot>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
