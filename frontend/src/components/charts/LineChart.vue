<script setup>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

const props = defineProps({
  data: { type: Object, default: () => ({}) }
})
</script>

<template>
  <Line :data="data" :options="{ responsive: true, maintainAspectRatio: false }" />
</template>
