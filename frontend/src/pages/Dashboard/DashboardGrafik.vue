<script setup>
import BaseCard from '../../components/common/BaseCard.vue'
import PieChart from '../../components/charts/PieChart.vue'
import LineChart from '../../components/charts/LineChart.vue'

const pieData = {
  labels: ['Program Berjalan', 'Program Selesai', 'Menunggu Approval'],
  datasets: [{ data: [48, 32, 20], backgroundColor: ['#3f7d20', '#fbbf24', '#94a3b8'] }]
}

const lineData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
  datasets: [{ label: 'Capaian', data: [20, 35, 30, 50, 60, 75], borderColor: '#3f7d20', tension: 0.35, fill: false }]
}
</script>

<template>
  <div class="space-y-6">
    <BaseCard title="Dashboard Grafik" subtitle="Visualisasi capaian dan status program">
      <div class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-2xl border border-slate-200 p-4">
          <h3 class="mb-3 text-sm font-semibold text-slate-700">Pie Chart Status</h3>
          <div class="h-72">
            <PieChart :data="pieData" />
          </div>
        </div>
        <div class="rounded-2xl border border-slate-200 p-4">
          <h3 class="mb-3 text-sm font-semibold text-slate-700">Line Chart Realisasi</h3>
          <div class="h-72">
            <LineChart :data="lineData" />
          </div>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
