<script setup>
import { onMounted, computed, ref } from 'vue'
import { useDashboardStore } from '../../store/dashboard'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'
import BaseTable from '../../components/common/BaseTable.vue'
import PieChart from '../../components/charts/PieChart.vue'
import LineChart from '../../components/charts/LineChart.vue'
import BarChart from '../../components/charts/BarChart.vue'
import {
  ArrowTrendingUpIcon,
  ClipboardDocumentListIcon,
  CurrencyDollarIcon,
  CheckCircleIcon,
  ClockIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'

const dashboardStore = useDashboardStore()
const stats = ref([])

// Stat cards computed from store or fallback values
const statItems = computed(() => [
  {
    title: 'Total Program',
    value: dashboardStore.statistik.total_program ?? 24,
    icon: ClipboardDocumentListIcon,
    color: 'text-pramuka-600',
    bg: 'bg-pramuka-50'
  },
  {
    title: 'Total Kegiatan',
    value: dashboardStore.statistik.total_kegiatan ?? 86,
    icon: ArrowTrendingUpIcon,
    color: 'text-amber-600',
    bg: 'bg-amber-50'
  },
  {
    title: 'Program Berjalan',
    value: dashboardStore.statistik.program_berjalan ?? 12,
    icon: ClockIcon,
    color: 'text-blue-600',
    bg: 'bg-blue-50'
  },
  {
    title: 'Program Selesai',
    value: dashboardStore.statistik.program_selesai ?? 8,
    icon: CheckCircleIcon,
    color: 'text-green-600',
    bg: 'bg-green-50'
  },
  {
    title: 'Menunggu Approval',
    value: dashboardStore.statistik.menunggu_approval ?? 4,
    icon: ClipboardDocumentListIcon,
    color: 'text-orange-600',
    bg: 'bg-orange-50'
  },
  {
    title: 'Total Anggaran',
    value: dashboardStore.statistik.total_anggaran ?? 'Rp 1,2 M',
    icon: CurrencyDollarIcon,
    color: 'text-purple-600',
    bg: 'bg-purple-50'
  },
  {
    title: 'Realisasi Anggaran',
    value: dashboardStore.statistik.realisasi_anggaran ?? 'Rp 980 Jt',
    icon: CurrencyDollarIcon,
    color: 'text-indigo-600',
    bg: 'bg-indigo-50'
  },
  {
    title: 'Persentase Capaian',
    value: dashboardStore.statistik.persentase_capaian ?? '82%',
    icon: ArrowTrendingUpIcon,
    color: 'text-emerald-600',
    bg: 'bg-emerald-50'
  }
])

// Summary table data
const summaryHeaders = ['Program', 'Target', 'Realisasi', 'Persentase', 'Status']
const summaryRows = computed(() => [
  { program: 'Program Paskibra', target: '18', realisasi: '16', persentase: '89%', status: 'Berjalan' },
  { program: 'Latihan Dasar', target: '12', realisasi: '10', persentase: '83%', status: 'Selesai' },
  { program: 'Kegiatan Sosial', target: '8', realisasi: '7', persentase: '88%', status: 'Menunggu Approval' },
  { program: 'Perkemahan Nasional', target: '20', realisasi: '18', persentase: '90%', status: 'Berjalan' }
])

// Chart data
const pieData = computed(() => ({
  labels: ['Berjalan', 'Selesai', 'Pending'],
  datasets: [{
    data: [
      dashboardStore.statistik.program_berjalan ?? 45,
      dashboardStore.statistik.program_selesai ?? 35,
      dashboardStore.statistik.menunggu_approval ?? 20
    ],
    backgroundColor: ['#3f7d20', '#fbbf24', '#94a3b8'],
    hoverOffset: 8
  }]
}))

const lineData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
  datasets: [{
    label: 'Realisasi Program',
    data: [14, 28, 22, 36, 40, 58],
    borderColor: '#3f7d20',
    backgroundColor: 'rgba(63,125,32,0.08)',
    tension: 0.4,
    fill: true,
    pointBackgroundColor: '#3f7d20'
  }]
}

const barData = {
  labels: ['Paskibra', 'Latihan Dasar', 'Sosial', 'Perkemahan'],
  datasets: [{
    label: 'Anggaran (Juta)',
    data: [300, 450, 220, 600],
    backgroundColor: ['#3f7d20', '#fbbf24', '#60a5fa', '#94a3b8'],
    borderRadius: 6
  }]
}

onMounted(async () => {
  await dashboardStore.getDashboard()
})
</script>

<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-pramuka-600">Ringkasan Operasional</p>
        <h2 class="mt-1 text-2xl font-semibold text-slate-900">Dashboard Pramuka Kwarda Jabar</h2>
        <p class="mt-1 max-w-2xl text-sm text-slate-500">
          Pantau capaian program secara cepat melalui metrik utama, grafik tren, dan tabel ringkasan.
        </p>
      </div>
      <BaseBadge variant="success" size="md">Live • Terakhir diperbarui</BaseBadge>
    </div>

    <!-- Stat cards -->
    <div v-if="dashboardStore.loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <BaseLoading v-for="i in 4" :key="i" />
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="item in statItems"
        :key="item.title"
        class="flex items-start gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft transition hover:shadow-md"
      >
        <div :class="['rounded-2xl p-3', item.bg, item.color]">
          <component :is="item.icon" class="h-6 w-6" />
        </div>
        <div class="min-w-0">
          <p class="truncate text-sm text-slate-500">{{ item.title }}</p>
          <p class="mt-1 text-xl font-semibold text-slate-900">{{ item.value }}</p>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="grid gap-6 xl:grid-cols-3">
      <BaseCard title="Status Program" subtitle="Distribusi berdasarkan status" class="xl:col-span-1">
        <div class="h-64">
          <PieChart :data="pieData" />
        </div>
      </BaseCard>
      <BaseCard title="Tren Realisasi" subtitle="Capaian program per bulan" class="xl:col-span-2">
        <div class="h-64">
          <LineChart :data="lineData" />
        </div>
      </BaseCard>
    </div>

    <!-- Bar chart full width -->
    <BaseCard title="Perbandingan Anggaran Program" subtitle="Alokasi anggaran per program (dalam juta rupiah)">
      <div class="h-64">
        <BarChart :data="barData" />
      </div>
    </BaseCard>

    <!-- Summary table -->
    <BaseCard title="Tabel Ringkasan Program" subtitle="Data program yang sedang dipantau">
      <BaseTable :headers="summaryHeaders" :rows="summaryRows" />
    </BaseCard>
  </div>
</template>
