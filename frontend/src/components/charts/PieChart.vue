<script setup>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const props = defineProps({
  data: { type: Object, default: () => ({}) }
})
</script>

<template>
  <Pie :data="data" :options="{ responsive: true, maintainAspectRatio: false }" />
</template>
