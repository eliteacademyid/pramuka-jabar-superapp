<template>
  <BaseTable :headers="headers" :rows="programs" :loading="loading">
    <template #default="{ row }">
      <!-- Custom row rendering -->
      <td class="px-4 py-3 text-sm text-slate-700 font-semibold">{{ row.nama }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.tahun }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.bidang || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.penanggung_jawab || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.target || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">{{ row.anggaran || '-' }}</td>
      <td class="px-4 py-3 text-sm text-slate-700">
        <span
          :class="[
            'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset',
            row.status === 'aktif'
              ? 'bg-green-50 text-green-700 ring-green-600/20'
              : row.status === 'selesai'
              ? 'bg-blue-50 text-blue-700 ring-blue-600/20'
              : 'bg-red-50 text-red-700 ring-red-600/20'
          ]"
        >
          {{ row.status }}
        </span>
      </td>
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
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['view', 'edit', 'delete'])

const headers = ['Nama', 'Tahun', 'Bidang', 'Penanggung Jawab', 'Target', 'Anggaran', 'Status', 'Aksi']
</script>

<style scoped>
/* No custom styles – rely on Tailwind utilities */
</style>
