<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  type: { type: String, default: 'info' },
  title: { type: String, default: '' },
  dismissible: { type: Boolean, default: false },
  autoDismiss: { type: Number, default: 0 }
})

const emit = defineEmits(['dismiss'])
const visible = ref(true)

function dismiss() {
  visible.value = false
  emit('dismiss')
}

onMounted(() => {
  if (props.autoDismiss > 0) {
    setTimeout(dismiss, props.autoDismiss)
  }
})

const styles = {
  info: 'border-blue-200 bg-blue-50 text-blue-700',
  success: 'border-green-200 bg-green-50 text-green-700',
  warning: 'border-amber-200 bg-amber-50 text-amber-700',
  danger: 'border-red-200 bg-red-50 text-red-700'
}
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" :class="['flex items-start gap-3 rounded-xl border px-4 py-3 text-sm leading-6', styles[type] || styles.info]">
      <div class="flex-1">
        <p v-if="title" class="mb-0.5 font-semibold">{{ title }}</p>
        <slot />
      </div>
      <button v-if="dismissible" class="flex-shrink-0 opacity-70 hover:opacity-100" @click="dismiss">✕</button>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
