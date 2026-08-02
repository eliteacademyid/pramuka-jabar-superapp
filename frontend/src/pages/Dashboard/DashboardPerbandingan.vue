<script setup>
import { onMounted, computed } from 'vue'
import { useDashboardStore } from '../../store/dashboard'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseAlert from '../../components/common/BaseAlert.vue'
import BaseTable from '../../components/common/BaseTable.vue'
import BarChart from '../../components/charts/BarChart.vue'

const store = useDashboardStore()

// Comparison bar chart: target vs realisasi
const barData = computed(() => {
  const items = store.perbandingan.length ? store.perbandingan : [
    { nama: 'Paskibra', target: 650, realisasi: 580 },
    { nama: 'Latihan Dasar', target: 450, realisasi: 400 },
    { nama: 'Kegiatan Sosial', target: 700, realisasi: 620 },
    { nama: 'Perkemahan', target: 520, realisasi: 490 }
  ]
  return {
    labels: items.map((i) => i.nama),
    datasets: [
      {
        label: 'Target (Juta)',
        data: items.map((i) => i.target),
        backgroundColor: '#94a3b8',
        borderRadius: 4
      },
      {
        label: 'Realisasi (Juta)',
        data: items.map((i) => i.realisasi),
        backgroundColor: '#3f7d20',
        borderRadius: 4
      }
    ]
  }
})

const tableHeaders = ['Program', 'Target (Juta)', 'Realisasi (Juta)', 'Selisih', 'Persentase']
const tableRows = computed(() => {
  const items = store.perbandingan.length ? store.perbandingan : [
    { nama: 'Paskibra', target: 650, realisasi: 580 },
    { nama: 'Latihan Dasar', target: 450, realisasi: 400 },
    { nama: 'Kegiatan Sosial', target: 700, realisasi: 620 },
    { nama: 'Perkemahan', target: 520, realisasi: 490 }
  ]
  return items.map((i) => ({
    nama: i.nama,
    target: `Rp ${i.target} Jt`,
    realisasi: `Rp ${i.realisasi} Jt`,
    selisih: `Rp ${i.target - i.realisasi} Jt`,
    persentase: `${Math.round((i.realisasi / i.target) * 100)}%`
  }))
})

onMounted(() => {
  store.getPerbandingan()
})
</script>

<template>
  <div class="space-y-6">
    <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-pramuka-600">Analisis Komparatif</p>
      <h2 class="mt-1 text-2xl font-semibold text-slate-900">Dashboard Perbandingan</h2>
      <p class="mt-1 text-sm text-slate-500">
        Bandingkan target anggaran dengan realisasi aktual per program secara visual dan tabular.
      </p>
    </div>

    <BaseAlert v-if="store.error" type="danger" dismissible>{{ store.error }}</BaseAlert>

    <BaseLoading v-if="store.loading" />

    <template v-else>
      <BaseCard title="Grafik Perbandingan Target vs Realisasi" subtitle="Alokasi anggaran dalam juta rupiah">
        <div class="h-80">
          <BarChart :data="barData" />
        </div>
      </BaseCard>

      <BaseCard title="Tabel Detail Perbandingan" subtitle="Rincian selisih target dan realisasi anggaran">
        <BaseTable :headers="tableHeaders" :rows="tableRows" />
      </BaseCard>

      <div class="grid gap-4 sm:grid-cols-3">
        <div v-for="item in [
          { label: 'Total Target', value: 'Rp 2,32 M', color: 'text-slate-700', bg: 'bg-slate-50' },
          { label: 'Total Realisasi', value: 'Rp 2,09 M', color: 'text-pramuka-700', bg: 'bg-pramuka-50' },
          { label: 'Rata-rata Capaian', value: '90,3%', color: 'text-green-700', bg: 'bg-green-50' }
        ]" :key="item.label" :class="['rounded-2xl border border-slate-200 p-5', item.bg]">
          <p class="text-xs text-slate-500">{{ item.label }}</p>
          <p :class="['mt-1 text-xl font-semibold', item.color]">{{ item.value }}</p>
        </div>
      </div>
    </template>
  </div>
</template>
