<template>
  <BaseSelect
    :options="yearOptions"
    placeholder="Pilih Tahun"
    v-model="selected"
    @update:modelValue="onChange"
    label="Tahun"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseSelect from '@/components/common/BaseSelect.vue'

const emit = defineEmits(['change'])

const selected = ref('')
const currentYear = new Date().getFullYear()

const yearOptions = computed(() => {
  const years = []
  for (let y = currentYear; y >= 2000; y--) {
    years.push({ value: y, label: String(y) })
  }
  return years
})

function onChange(value) {
  emit('change', value)
}
</script>

<style scoped>
/* No custom styles – rely on Tailwind */
</style>
