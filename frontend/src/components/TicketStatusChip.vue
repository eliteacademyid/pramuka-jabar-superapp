<template>
  <span class="badge" :class="'status-' + status">{{ label }}</span>
</template>

<script setup>
const props = defineProps({
  status: { type: String, required: true }
})

const LABELS = {
  open: 'Dibuka',
  in_review: 'Ditinjau',
  resolved: 'Diselesaikan',
  closed: 'Ditutup'
}

const label = LABELS[props.status] || props.status
</script>
