<template>
  <BaseSearch placeholder="Cari program..." @search="onSearch" />
</template>

<script setup>
import BaseSearch from '@/components/common/BaseSearch.vue'
const emit = defineEmits(['search'])
function onSearch(value) {
  emit('search', value)
}
</script>

<style scoped>
/* No custom styles */
</style>
