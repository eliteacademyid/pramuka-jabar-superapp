<script setup>
import { onMounted, computed } from 'vue'
import { useDashboardStore } from '../../store/dashboard'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseAlert from '../../components/common/BaseAlert.vue'
import PieChart from '../../components/charts/PieChart.vue'
import LineChart from '../../components/charts/LineChart.vue'

const store = useDashboardStore()

const pieData = computed(() => ({
  labels: ['Program Berjalan', 'Program Selesai', 'Menunggu Approval'],
  datasets: [{
    data: [
      store.statistik.program_berjalan ?? 48,
      store.statistik.program_selesai ?? 32,
      store.statistik.menunggu_approval ?? 20
    ],
    backgroundColor: ['#3f7d20', '#fbbf24', '#94a3b8'],
    borderWidth: 0,
    hoverOffset: 8
  }]
}))

const lineData = computed(() => {
  const rawData = store.grafik?.bulanan ?? [20, 35, 30, 50, 60, 75]
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
    datasets: [{
      label: 'Capaian Program',
      data: rawData,
      borderColor: '#3f7d20',
      backgroundColor: 'rgba(63,125,32,0.1)',
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#3f7d20',
      pointRadius: 5
    }]
  }
})

onMounted(() => {
  store.getStatistik()
  store.getGrafik()
})
</script>

<template>
  <div class="space-y-6">
    <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-pramuka-600">Visualisasi Data</p>
      <h2 class="mt-1 text-2xl font-semibold text-slate-900">Dashboard Grafik</h2>
      <p class="mt-1 text-sm text-slate-500">Visualisasi capaian dan distribusi status program secara grafik interaktif.</p>
    </div>

    <BaseAlert v-if="store.error" type="danger" dismissible>{{ store.error }}</BaseAlert>

    <BaseLoading v-if="store.loading" />

    <div v-else class="grid gap-6 xl:grid-cols-2">
      <BaseCard title="Distribusi Status Program" subtitle="Proporsi berdasarkan status saat ini">
        <div class="h-80">
          <PieChart :data="pieData" />
        </div>
      </BaseCard>

      <BaseCard title="Tren Capaian Bulanan" subtitle="Perkembangan realisasi program per bulan">
        <div class="h-80">
          <LineChart :data="lineData" />
        </div>
      </BaseCard>
    </div>

    <BaseCard title="Interpretasi Grafik" subtitle="Catatan analisis data">
      <div class="grid gap-4 sm:grid-cols-3">
        <div v-for="item in [
          { label: 'Program Dominan', value: 'Berjalan (48%)', color: 'text-pramuka-600', bg: 'bg-pramuka-50' },
          { label: 'Tren Capaian', value: 'Meningkat +15%', color: 'text-green-600', bg: 'bg-green-50' },
          { label: 'Bulan Terbaik', value: 'Juni — 75 capaian', color: 'text-blue-600', bg: 'bg-blue-50' }
        ]" :key="item.label" :class="['rounded-xl p-4', item.bg]">
          <p class="text-xs text-slate-500">{{ item.label }}</p>
          <p :class="['mt-1 text-sm font-semibold', item.color]">{{ item.value }}</p>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
