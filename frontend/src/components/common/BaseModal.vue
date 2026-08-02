<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Modal' },
  size: { type: String, default: 'md' },
  persistent: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

function close() {
  if (!props.persistent) {
    emit('update:modelValue', false)
  }
}

const sizeClass = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl'
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 px-4 py-8"
        @click.self="close"
      >
        <div :class="['w-full rounded-2xl bg-white shadow-2xl', sizeClass[size] || sizeClass.md]">
          <div class="flex items-start justify-between border-b border-slate-100 px-6 py-4">
            <h3 class="text-lg font-semibold text-slate-800">{{ title }}</h3>
            <button
              class="rounded-lg p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
              @click="close"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
          <div class="px-6 py-5">
            <slot />
          </div>
          <div v-if="$slots.footer" class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
