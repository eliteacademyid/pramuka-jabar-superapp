<script setup>
import BaseCard from '../../components/common/BaseCard.vue'
import BarChart from '../../components/charts/BarChart.vue'

const barData = {
  labels: ['Program A', 'Program B', 'Program C', 'Program D'],
  datasets: [{ label: 'Target vs Realisasi', data: [600, 450, 700, 520], backgroundColor: ['#3f7d20', '#fbbf24', '#60a5fa', '#94a3b8'] }]
}
</script>

<template>
  <div class="space-y-6">
    <BaseCard title="Dashboard Perbandingan" subtitle="Bandingkan target anggaran dan realisasi program">
      <div class="h-80">
        <BarChart :data="barData" />
      </div>
    </BaseCard>
  </div>
</template>
