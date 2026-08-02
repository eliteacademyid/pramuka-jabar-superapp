<template>
  <BasePagination
    :current-page="currentPage"
    :total-pages="totalPages"
    :total-items="totalItems"
    :per-page="perPage"
    @change="onChange"
  />
</template>

<script setup>
import BasePagination from '@/components/common/BasePagination.vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  totalPages: { type: Number, default: 1 },
  totalItems: { type: Number, default: 0 },
  perPage: { type: Number, default: 10 }
})

const emit = defineEmits(['change'])

function onChange(page) {
  emit('change', page)
}
</script>

<style scoped>
/* No custom styles */
</style>
