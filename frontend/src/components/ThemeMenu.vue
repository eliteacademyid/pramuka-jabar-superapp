<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useTheme } from '../composables/useTheme'

defineProps({
  tone: { type: String, default: 'bar' }
})

const { theme, setTheme } = useTheme()
const open = ref(false)

function toggle() {
  open.value = !open.value
}

function pick(t) {
  setTheme(t)
  open.value = false
}

function onDocClick(e) {
  if (!e.target.closest('.theme-menu')) open.value = false
}

onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<template>
  <div class="theme-menu" :class="`theme-menu--${tone}`">
    <button
      class="theme-menu-btn"
      type="button"
      :title="theme === 'dark' ? 'Tema: Gelap' : theme === 'blue' ? 'Tema: Biru' : 'Tema: Default'"
      @click="toggle"
    >
      <i class="fas" :class="theme === 'dark' ? 'fa-moon' : theme === 'blue' ? 'fa-palette' : 'fa-sun'"></i>
      <span>Tema</span>
      <i class="fas fa-chevron-down theme-menu-caret"></i>
    </button>
    <div v-if="open" class="theme-menu-dropdown">
      <p class="theme-menu-label">Pilih tema</p>
      <button
        type="button"
        class="theme-menu-option"
        :class="{ active: theme === 'default' }"
        @click="pick('default')"
      >
        <i class="fas fa-sun"></i>
        <span>Default <small>terang</small></span>
        <i v-if="theme === 'default'" class="fas fa-check"></i>
      </button>
      <button
        type="button"
        class="theme-menu-option"
        :class="{ active: theme === 'dark' }"
        @click="pick('dark')"
      >
        <i class="fas fa-moon"></i>
        <span>Gelap <small>dark</small></span>
        <i v-if="theme === 'dark'" class="fas fa-check"></i>
      </button>
      <button
        type="button"
        class="theme-menu-option"
        :class="{ active: theme === 'blue' }"
        @click="pick('blue')"
      >
        <i class="fas fa-palette"></i>
        <span>Biru <small>cerah</small></span>
        <i v-if="theme === 'blue'" class="fas fa-check"></i>
      </button>
    </div>
  </div>
</template>
