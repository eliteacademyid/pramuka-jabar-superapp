<script setup>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  data: { type: Object, default: () => ({ labels: [], datasets: [] }) },
  options: { type: Object, default: () => ({}) },
  horizontal: { type: Boolean, default: false }
})

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      labels: { padding: 16, font: { size: 12 } }
    },
    tooltip: { enabled: true }
  },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } }
  }
}
</script>

<template>
  <Bar
    :data="data"
    :options="{
      ...defaultOptions,
      ...options,
      indexAxis: horizontal ? 'y' : 'x'
    }"
  />
</template>
