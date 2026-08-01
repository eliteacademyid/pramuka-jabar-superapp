<template>
  <span class="badge" :class="'status-' + status">{{ label }}</span>
</template>

<script setup>
const props = defineProps({
  status: { type: String, required: true }
})

const LABELS = {
  pending_payment: 'Menunggu Bayar',
  paid: 'Dibayar',
  processed: 'Diproses',
  shipped: 'Dikirim',
  delivered: 'Diterima',
  completed: 'Selesai',
  cancelled: 'Dibatalkan',
  refunded: 'Refund'
}

const label = LABELS[props.status] || props.status
</script>
