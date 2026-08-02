<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Program List</h1>
    <!-- Year Filter -->
    <ProgramYearFilter @change="onYearChange" class="mb-4" />
    <!-- Placeholder for table, will be added in later tasks -->
    <p class="text-gray-600">Table will appear here.</p>
  </div>
</template>

<script setup>
import ProgramYearFilter from '@/components/ProgramYearFilter.vue'

const emit = defineEmits(['yearFilter'])

function onYearChange(year) {
  emit('yearFilter', year)
}
</script>

<style scoped>
/* No custom styles – rely on Tailwind */
</style>
