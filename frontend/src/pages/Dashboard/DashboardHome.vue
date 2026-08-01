<script setup>
import { onMounted, computed, ref } from 'vue'
import { useDashboardStore } from '../../store/dashboard'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'
import PieChart from '../../components/charts/PieChart.vue'
import LineChart from '../../components/charts/LineChart.vue'
import BarChart from '../../components/charts/BarChart.vue'
import BaseTable from '../../components/common/BaseTable.vue'
import { ArrowTrendingUpIcon, ClipboardDocumentListIcon, CurrencyDollarIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'

const dashboardStore = useDashboardStore()
const stats = ref([])

const summaryRows = computed(() => [
  { program: 'Program Paskibra', target: '18', realisasi: '16', persentase: '89%', status: 'Berjalan' },
  { program: 'Latihan Dasar', target: '12', realisasi: '10', persentase: '83%', status: 'Selesai' },
  { program: 'Kegiatan Sosial', target: '8', realisasi: '7', persentase: '88%', status: 'Menunggu Approval' }
])

onMounted(async () => {
  await dashboardStore.getDashboard()
  stats.value = [
    { title: 'Total Program', value: dashboardStore.statistik.total_program || '24', icon: ClipboardDocumentListIcon, color: 'text-pramuka-600' },
    { title: 'Total Kegiatan', value: dashboardStore.statistik.total_kegiatan || '86', icon: ArrowTrendingUpIcon, color: 'text-amber-600' },
    { title: 'Program Berjalan', value: dashboardStore.statistik.program_berjalan || '12', icon: ClipboardDocumentListIcon, color: 'text-blue-600' },
    { title: 'Program Selesai', value: dashboardStore.statistik.program_selesai || '8', icon: CheckCircleIcon, color: 'text-green-600' },
    { title: 'Menunggu Approval', value: dashboardStore.statistik.menunggu_approval || '4', icon: ClipboardDocumentListIcon, color: 'text-orange-600' },
    { title: 'Total Anggaran', value: dashboardStore.statistik.total_anggaran || 'Rp 1.2 M', icon: CurrencyDollarIcon, color: 'text-purple-600' },
    { title: 'Realisasi Anggaran', value: dashboardStore.statistik.realisasi_anggaran || 'Rp 980 Jt', icon: CurrencyDollarIcon, color: 'text-indigo-600' },
    { title: 'Persentase Capaian', value: dashboardStore.statistik.persentase_capaian || '82%', icon: ArrowTrendingUpIcon, color: 'text-emerald-600' }
  ]
})

const pieData = {
  labels: ['Berjalan', 'Selesai', 'Pending'],
  datasets: [{ data: [45, 35, 20], backgroundColor: ['#3f7d20', '#fbbf24', '#94a3b8'] }]
}

const lineData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
  datasets: [{ label: 'Realisasi', data: [14, 28, 22, 36, 40, 58], borderColor: '#3f7d20', tension: 0.35, fill: false }]
}

const barData = {
  labels: ['Program A', 'Program B', 'Program C', 'Program D'],
  datasets: [{ label: 'Anggaran', data: [300, 450, 220, 600], backgroundColor: ['#3f7d20', '#fbbf24', '#60a5fa', '#94a3b8'] }]
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-pramuka-600">Ringkasan Operasional</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">Dashboard utama Pramuka Jabar</h2>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">Pantau capaiannya secara cepat melalui metrik utama, grafik, dan tabel ringkasan program.</p>
      </div>
      <BaseBadge variant="success">Live • Terakhir diperbarui</BaseBadge>
    </div>

    <div v-if="dashboardStore.loading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <BaseLoading v-for="i in 4" :key="i" />
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <BaseCard v-for="item in stats" :key="item.title" class="flex items-start gap-4">
        <div :class="['rounded-2xl bg-slate-50 p-3', item.color]">
          <component :is="item.icon" class="h-6 w-6" />
        </div>
        <div>
          <p class="text-sm text-slate-500">{{ item.title }}</p>
          <p class="mt-1 text-xl font-semibold text-slate-900">{{ item.value }}</p>
        </div>
      </BaseCard>
    </div>

    <div class="grid gap-6 xl:grid-cols-3">
      <BaseCard title="Status Program" subtitle="Distribusi berdasarkan status" class="xl:col-span-1">
        <div class="h-64">
          <PieChart :data="pieData" />
        </div>
      </BaseCard>
      <BaseCard title="Realisasi Program" subtitle="Tren capaian bulanan" class="xl:col-span-2">
        <div class="h-64">
          <LineChart :data="lineData" />
        </div>
      </BaseCard>
      <BaseCard title="Anggaran Program" subtitle="Perbandingan alokasi anggaran" class="xl:col-span-3">
        <div class="h-64">
          <BarChart :data="barData" />
        </div>
      </BaseCard>
    </div>

    <BaseCard title="Tabel Ringkasan Program" subtitle="Data program yang sedang dipantau">
      <BaseTable :headers="['Program', 'Target', 'Realisasi', 'Persentase', 'Status']" :rows="summaryRows" />
    </BaseCard>
  </div>
</template>
