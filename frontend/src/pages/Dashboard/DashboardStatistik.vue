<script setup>
import BaseCard from '../../components/common/BaseCard.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'
</script>

<template>
  <div class="space-y-6">
    <BaseCard title="Dashboard Statistik" subtitle="Metrik inti per area operasional">
      <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div v-for="item in [
          { label: 'Total Program', value: '24', badge: 'Aktif' },
          { label: 'Total Kegiatan', value: '86', badge: 'Terlaksana' },
          { label: 'Program Berjalan', value: '12', badge: 'On Track' },
          { label: 'Program Selesai', value: '8', badge: 'Selesai' }
        ]" :key="item.label" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p class="text-sm text-slate-500">{{ item.label }}</p>
          <div class="mt-2 flex items-end justify-between">
            <p class="text-2xl font-semibold text-slate-900">{{ item.value }}</p>
            <BaseBadge variant="success">{{ item.badge }}</BaseBadge>
          </div>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
