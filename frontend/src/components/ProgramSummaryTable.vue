<script setup>
import BaseBadge from './common/BaseBadge.vue'

defineProps({
  rows: {
    type: Array,
    default: () => []
  }
})

function statusVariant(status) {
  if (!status) return 'default'
  const s = status.toLowerCase()
  if (s.includes('selesai')) return 'success'
  if (s.includes('berjalan')) return 'info'
  if (s.includes('approval') || s.includes('menunggu')) return 'warning'
  return 'default'
}

function pctColor(pct) {
  const n = parseInt(pct)
  if (n >= 90) return 'bg-green-500'
  if (n >= 70) return 'bg-amber-500'
  return 'bg-red-500'
}
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Program</th>
            <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-600">Target</th>
            <th class="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-600">Realisasi</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Persentase</th>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="rows.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-sm text-slate-400">Tidak ada data program.</td>
          </tr>
          <tr v-for="row in rows" :key="row.program" class="hover:bg-slate-50">
            <td class="px-4 py-3 text-sm font-medium text-slate-800">{{ row.program }}</td>
            <td class="px-4 py-3 text-right text-sm text-slate-600">{{ row.target }}</td>
            <td class="px-4 py-3 text-right text-sm text-slate-600">{{ row.realisasi }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="h-1.5 w-20 overflow-hidden rounded-full bg-slate-200">
                  <div
                    :class="['h-full rounded-full', pctColor(row.persentase)]"
                    :style="{ width: row.persentase }"
                  ></div>
                </div>
                <span class="text-xs font-medium text-slate-700">{{ row.persentase }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <BaseBadge :variant="statusVariant(row.status)">{{ row.status }}</BaseBadge>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
