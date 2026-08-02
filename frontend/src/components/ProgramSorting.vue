<template>
  <BaseSelect
    :options="sortOptions"
    placeholder="Urutkan"
    v-model="selected"
    @update:modelValue="onChange"
    label="Urutkan"
  />
</template>

<script setup>
import { ref } from 'vue'
import BaseSelect from '@/components/common/BaseSelect.vue'

const emit = defineEmits(['change'])

const selected = ref('tahun_desc') // Default sort: Terbaru
const sortOptions = [
  { value: 'nama_asc', label: 'Nama (A-Z)' },
  { value: 'nama_desc', label: 'Nama (Z-A)' },
  { value: 'tahun_desc', label: 'Tahun (Terbaru)' },
  { value: 'tahun_asc', label: 'Tahun (Terlama)' },
  { value: 'status_asc', label: 'Status' }
]

function onChange(value) {
  let orderBy = 'tahun'
  let orderDir = 'desc'

  if (value === 'nama_asc') {
    orderBy = 'nama'
    orderDir = 'asc'
  } else if (value === 'nama_desc') {
    orderBy = 'nama'
    orderDir = 'desc'
  } else if (value === 'tahun_asc') {
    orderBy = 'tahun'
    orderDir = 'asc'
  } else if (value === 'tahun_desc') {
    orderBy = 'tahun'
    orderDir = 'desc'
  } else if (value === 'status_asc') {
    orderBy = 'status'
    orderDir = 'asc'
  }

  emit('change', { order_by: orderBy, order_dir: orderDir })
}
</script>

<style scoped>
/* No custom styles – rely on Tailwind */
</style>
