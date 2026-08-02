<template>
  <BaseTable :headers="headers" :rows="programs">
    <template #default="{ row }">
      <!-- Custom row rendering -->
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.nama }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.tahun }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.bidang || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.penanggung_jawab || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.target || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.anggaran || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.status }}</td>
      <td class="px-4 py-3 text-sm text-slate-700 space-x-2">
        <BaseButton size="sm" @click="$emit('view', row.id)">Detail</BaseButton>
        <BaseButton size="sm" @click="$emit('edit', row.id)">Edit</BaseButton>
        <BaseButton size="sm" variant="danger" @click="$emit('delete', row.id)">Delete</BaseButton>
      </td>
    </template>
  </BaseTable>
</template>

<script setup>
import BaseTable from '@/components/common/BaseTable.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const props = defineProps({
  programs: { type: Array, default: () => [] },
})

const emit = defineEmits(['view', 'edit', 'delete'])

const headers = ['Nama', 'Tahun', 'Bidang', 'Penanggung Jawab', 'Target', 'Anggaran', 'Status', 'Aksi']
</script>

<style scoped>
/* No custom styles – rely on Tailwind utilities */
</style>
