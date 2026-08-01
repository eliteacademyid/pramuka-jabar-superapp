<script setup>
const props = defineProps({
  show: { type: Boolean, default: false },
  type: { type: String, default: 'success' }, // 'success' | 'error' | 'warning'
  title: { type: String, default: '' },
  message: { type: String, default: '' },
})

const emit = defineEmits(['close'])
</script>

<template>
  <Transition name="modal">
    <div v-if="show" class="modal-overlay" @click.self="emit('close')">
      <div :class="['modal-card', `modal-${type}`]">
        <!-- Icon -->
        <div :class="['modal-icon-wrap', `icon-${type}`]">
          <svg v-if="type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6L9 17l-5-5"/>
          </svg>
          <svg v-else-if="type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          </svg>
        </div>

        <!-- Text -->
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-message">{{ message }}</p>

        <!-- Button -->
        <button :class="['modal-btn', `btn-${type}`]" @click="emit('close')">
          OK, Tutup
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
  padding: 1.5rem;
}

.modal-card {
  background: white;
  border-radius: 24px;
  padding: 2.5rem 2rem;
  width: 100%; max-width: 380px;
  text-align: center;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.2);
  position: relative;
  overflow: hidden;
}

.modal-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 5px;
}
.modal-success::before { background: linear-gradient(90deg, #4ade80, #16a34a); }
.modal-error::before   { background: linear-gradient(90deg, #f87171, #dc2626); }
.modal-warning::before { background: linear-gradient(90deg, #fbbf24, #d97706); }

/* Icon */
.modal-icon-wrap {
  width: 64px; height: 64px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.25rem;
}
.modal-icon-wrap svg {
  width: 30px; height: 30px;
}
.icon-success { background: #dcfce7; color: #16a34a; }
.icon-error   { background: #fee2e2; color: #dc2626; }
.icon-warning { background: #fef9c3; color: #d97706; }

/* Text */
.modal-title {
  font-size: 1.25rem; font-weight: 800;
  color: #111827; margin: 0 0 0.5rem;
}
.modal-message {
  font-size: 0.9rem; color: #6b7280;
  line-height: 1.6; margin: 0 0 1.75rem;
}

/* Button */
.modal-btn {
  display: block; width: 100%;
  padding: 0.8rem 1.5rem;
  border: none; border-radius: 12px;
  font-size: 0.95rem; font-weight: 700;
  cursor: pointer; transition: all 0.2s;
  color: white;
}
.btn-success { background: linear-gradient(135deg, #16a34a, #15803d); box-shadow: 0 4px 12px rgba(22,163,74,0.3); }
.btn-error   { background: linear-gradient(135deg, #dc2626, #b91c1c); box-shadow: 0 4px 12px rgba(220,38,38,0.3); }
.btn-warning { background: linear-gradient(135deg, #d97706, #b45309); box-shadow: 0 4px 12px rgba(217,119,6,0.3); }
.modal-btn:hover { transform: translateY(-1px); filter: brightness(1.05); }

/* Transition */
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-card, .modal-leave-to .modal-card {
  transform: scale(0.88) translateY(20px);
}
</style>
