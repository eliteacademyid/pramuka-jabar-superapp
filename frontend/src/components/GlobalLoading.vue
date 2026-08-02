<script setup>
import { useGlobalStore } from '../store/global'
import { storeToRefs } from 'pinia'

const globalStore = useGlobalStore()
const { loading, loadingMessage } = storeToRefs(globalStore)
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="loading"
        class="fixed inset-0 z-[9999] flex items-center justify-center bg-white/70 backdrop-blur-sm"
        role="status"
        aria-live="polite"
        aria-label="Sedang memuat"
      >
        <div class="flex flex-col items-center gap-4 rounded-2xl bg-white px-8 py-6 shadow-2xl">
          <div class="relative h-12 w-12">
            <div class="absolute inset-0 animate-spin rounded-full border-4 border-pramuka-100 border-t-pramuka-600"></div>
          </div>
          <p class="text-sm font-medium text-slate-700">{{ loadingMessage || 'Memuat...' }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
