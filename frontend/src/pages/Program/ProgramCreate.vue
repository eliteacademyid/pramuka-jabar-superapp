<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center gap-4">
      <h1 class="text-2xl font-bold text-slate-800">Tambah Program</h1>
    </div>

    <!-- Form component -->
    <ProgramForm
      mode="create"
      :saving="saving"
      @submit="onSubmit"
      @cancel="onCancel"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProgramStore } from '@/store/program'
import { useGlobalStore } from '@/store/global'
import ProgramForm from '@/components/ProgramForm.vue'

const router = useRouter()
const programStore = useProgramStore()
const globalStore = useGlobalStore()
const saving = ref(false)

async function onSubmit(payload) {
  saving.value = true
  try {
    await programStore.addProgram(payload)
    globalStore.toast.success('Program berhasil ditambahkan')
    router.push({ name: 'programs' })
  } catch (err) {
    globalStore.toast.error(err.response?.data?.detail || 'Gagal menambahkan program')
    console.error('Failed to create program:', err)
  } finally {
    saving.value = false
  }
}

function onCancel() {
  router.push({ name: 'programs' })
}
</script>

<style scoped>
/* No custom styles */
</style>
