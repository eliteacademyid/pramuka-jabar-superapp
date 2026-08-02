<script setup>
import { onMounted, computed } from 'vue'
import { useDashboardStore } from '../../store/dashboard'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseAlert from '../../components/common/BaseAlert.vue'
import {
  ClipboardDocumentListIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const store = useDashboardStore()

const metrics = computed(() => [
  {
    label: 'Total Program',
    value: store.statistik.total_program ?? 24,
    badge: 'Aktif',
    badgeVariant: 'success',
    icon: ClipboardDocumentListIcon,
    description: 'Jumlah seluruh program yang terdaftar'
  },
  {
    label: 'Total Kegiatan',
    value: store.statistik.total_kegiatan ?? 86,
    badge: 'Terlaksana',
    badgeVariant: 'info',
    icon: ArrowTrendingUpIcon,
    description: 'Total kegiatan dari semua program'
  },
  {
    label: 'Program Berjalan',
    value: store.statistik.program_berjalan ?? 12,
    badge: 'On Track',
    badgeVariant: 'warning',
    icon: ClockIcon,
    description: 'Program yang sedang dalam pelaksanaan'
  },
  {
    label: 'Program Selesai',
    value: store.statistik.program_selesai ?? 8,
    badge: 'Selesai',
    badgeVariant: 'success',
    icon: CheckCircleIcon,
    description: 'Program yang telah selesai dilaksanakan'
  }
])

onMounted(() => {
  store.getStatistik()
})
</script>

<template>
  <div class="space-y-6">
    <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-pramuka-600">Statistik</p>
      <h2 class="mt-1 text-2xl font-semibold text-slate-900">Dashboard Statistik</h2>
      <p class="mt-1 text-sm text-slate-500">Metrik inti operasional per area program Pramuka Kwarda Jabar.</p>
    </div>

    <BaseAlert v-if="store.error" type="danger" dismissible>{{ store.error }}</BaseAlert>

    <div v-if="store.loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <BaseLoading v-for="i in 4" :key="i" />
    </div>

    <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="item in metrics"
        :key="item.label"
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft transition hover:shadow-md"
      >
        <div class="flex items-start justify-between">
          <div class="rounded-xl bg-pramuka-50 p-2.5 text-pramuka-600">
            <component :is="item.icon" class="h-5 w-5" />
          </div>
          <BaseBadge :variant="item.badgeVariant">{{ item.badge }}</BaseBadge>
        </div>
        <p class="mt-4 text-2xl font-semibold text-slate-900">{{ item.value }}</p>
        <p class="mt-1 text-sm font-medium text-slate-700">{{ item.label }}</p>
        <p class="mt-0.5 text-xs text-slate-400">{{ item.description }}</p>
      </div>
    </div>

    <div class="grid gap-6 sm:grid-cols-2">
      <BaseCard title="Ringkasan Anggaran" subtitle="Alokasi dan realisasi anggaran program">
        <div class="space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Total Anggaran</span>
            <span class="font-semibold text-slate-900">{{ store.statistik.total_anggaran ?? 'Rp 1,2 M' }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-slate-600">Realisasi</span>
            <span class="font-semibold text-green-700">{{ store.statistik.realisasi_anggaran ?? 'Rp 980 Jt' }}</span>
          </div>
          <div class="mt-2">
            <div class="mb-1 flex justify-between text-xs text-slate-500">
              <span>Persentase Capaian</span>
              <span>{{ store.statistik.persentase_capaian ?? '82%' }}</span>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-slate-200">
              <div class="h-full rounded-full bg-pramuka-600" style="width: 82%"></div>
            </div>
          </div>
        </div>
      </BaseCard>

      <BaseCard title="Persentase Keterlaksanaan" subtitle="Capaian program terhadap target">
        <div class="space-y-3">
          <div v-for="item in [
            { label: 'Paskibra', pct: 89 },
            { label: 'Latihan Dasar', pct: 83 },
            { label: 'Kegiatan Sosial', pct: 88 },
            { label: 'Perkemahan', pct: 90 }
          ]" :key="item.label">
            <div class="mb-1 flex justify-between text-xs text-slate-600">
              <span>{{ item.label }}</span>
              <span class="font-semibold">{{ item.pct }}%</span>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-slate-200">
              <div
                class="h-full rounded-full bg-pramuka-600 transition-all duration-700"
                :style="{ width: item.pct + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>
