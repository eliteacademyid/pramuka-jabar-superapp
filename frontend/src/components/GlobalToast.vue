<script setup>
import { useGlobalStore } from '../store/global'
import { storeToRefs } from 'pinia'

const globalStore = useGlobalStore()
const { toasts } = storeToRefs(globalStore)

const typeStyles = {
  success: 'border-green-200 bg-green-50 text-green-800',
  error: 'border-red-200 bg-red-50 text-red-800',
  warning: 'border-amber-200 bg-amber-50 text-amber-800',
  info: 'border-blue-200 bg-blue-50 text-blue-800'
}

const typeIcons = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ'
}
</script>

<template>
  <Teleport to="body">
    <div
      aria-live="assertive"
      class="pointer-events-none fixed inset-0 z-[9998] flex flex-col items-end justify-start gap-3 px-4 py-6 sm:px-6 sm:py-8"
    >
      <TransitionGroup name="toast" tag="div" class="flex flex-col items-end gap-3">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-2xl border px-4 py-3 shadow-soft',
            typeStyles[toast.type] || typeStyles.info
          ]"
          role="alert"
        >
          <span class="mt-0.5 flex-shrink-0 font-bold">{{ typeIcons[toast.type] || typeIcons.info }}</span>
          <p class="flex-1 text-sm font-medium leading-5">{{ toast.message }}</p>
          <button
            class="flex-shrink-0 opacity-60 transition hover:opacity-100"
            @click="globalStore.removeToast(toast.id)"
            aria-label="Tutup notifikasi"
          >
            ✕
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from { opacity: 0; transform: translateX(60px) scale(0.9); }
.toast-leave-to { opacity: 0; transform: translateX(60px); }
.toast-move { transition: transform 0.3s ease; }
</style>
