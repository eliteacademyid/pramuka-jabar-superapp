<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center gap-4">
      <h1 class="text-2xl font-bold text-slate-800">Edit Program</h1>
    </div>

    <!-- Show loader while fetching -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-pramuka-600"></div>
    </div>

    <!-- Form component once data is ready -->
    <ProgramForm
      v-else-if="programData"
      mode="edit"
      :initial-data="programData"
      :saving="saving"
      @submit="onSubmit"
      @cancel="onCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProgramStore } from '@/store/program'
import { useGlobalStore } from '@/store/global'
import ProgramForm from '@/components/ProgramForm.vue'

const route = useRoute()
const router = useRouter()
const programStore = useProgramStore()
const globalStore = useGlobalStore()

const loading = ref(true)
const saving = ref(false)
const programData = ref(null)

onMounted(async () => {
  const id = Number(route.params.id)
  try {
    const data = await programStore.fetchProgramById(id)
    programData.value = data
  } catch (err) {
    globalStore.toast.error('Gagal memuat data program.')
    router.push({ name: 'programs' })
  } finally {
    loading.value = false
  }
})

async function onSubmit(payload) {
  const id = Number(route.params.id)
  saving.value = true
  try {
    await programStore.editProgram(id, payload)
    globalStore.toast.success('Program berhasil diperbarui')
    router.push({ name: 'programs' })
  } catch (err) {
    globalStore.toast.error(err.response?.data?.detail || 'Gagal memperbarui program')
    console.error('Failed to update program:', err)
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
