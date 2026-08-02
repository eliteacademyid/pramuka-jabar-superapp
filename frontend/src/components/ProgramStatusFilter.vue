<template>
  <BaseSelect
    :options="statusOptions"
    placeholder="Pilih Status"
    v-model="selected"
    @update:modelValue="onChange"
    label="Status"
  />
</template>

<script setup>
import { ref } from 'vue'
import BaseSelect from '@/components/common/BaseSelect.vue'

const emit = defineEmits(['change'])

const selected = ref('')
const statusOptions = [
  { value: 'aktif', label: 'Aktif' },
  { value: 'selesai', label: 'Selesai' },
  { value: 'ditangguhkan', label: 'Ditangguhkan' }
]

function onChange(value) {
  emit('change', value)
}
</script>

<style scoped>
/* No custom styles – rely on Tailwind */
</style>
