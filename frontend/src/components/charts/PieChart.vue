<script setup>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const props = defineProps({
  data: { type: Object, default: () => ({ labels: [], datasets: [] }) },
  options: { type: Object, default: () => ({}) }
})

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { padding: 16, font: { size: 12 } }
    },
    tooltip: { enabled: true }
  }
}
</script>

<template>
  <Pie :data="data" :options="{ ...defaultOptions, ...options }" />
</template>
