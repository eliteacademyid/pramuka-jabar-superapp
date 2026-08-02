import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * Global store — shared UI state used across the entire application.
 * Task 7.1 — Sidebar state
 * Task 7.2 — Global loading state
 * Task 7.3 — Global toast notification
 * Task 7.4 — Dark mode support (optional)
 */
export const useGlobalStore = defineStore('global', () => {
  // ── Task 7.1: Sidebar state ───────────────────────────────────────────────
  const sidebarCollapsed = ref(false)
  const sidebarMobileOpen = ref(false)

  function setSidebarCollapsed(value) {
    sidebarCollapsed.value = value
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function toggleMobileSidebar() {
    sidebarMobileOpen.value = !sidebarMobileOpen.value
  }

  function closeMobileSidebar() {
    sidebarMobileOpen.value = false
  }

  // ── Task 7.2: Global loading state ───────────────────────────────────────
  const loading = ref(false)
  const loadingMessage = ref('')

  function setLoading(value, message = '') {
    loading.value = value
    loadingMessage.value = message
  }

  function startLoading(message = 'Memuat...') {
    loading.value = true
    loadingMessage.value = message
  }

  function stopLoading() {
    loading.value = false
    loadingMessage.value = ''
  }

  // ── Task 7.3: Global toast notification ───────────────────────────────────
  const toasts = ref([])
  let toastIdCounter = 0

  function addToast(message, type = 'success', duration = 4000) {
    const id = ++toastIdCounter
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
    return id
  }

  function removeToast(id) {
    const idx = toasts.value.findIndex((t) => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  function clearToasts() {
    toasts.value = []
  }

  /** Convenience helpers */
  const toast = {
    success: (msg, duration) => addToast(msg, 'success', duration),
    error: (msg, duration) => addToast(msg, 'error', duration),
    warning: (msg, duration) => addToast(msg, 'warning', duration),
    info: (msg, duration) => addToast(msg, 'info', duration)
  }

  // ── Task 7.4: Dark mode (optional) ────────────────────────────────────────
  const darkMode = ref(
    localStorage.getItem('darkMode') === 'true' ||
    window.matchMedia('(prefers-color-scheme: dark)').matches
  )

  const isDark = computed(() => darkMode.value)

  function toggleDarkMode() {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value)
    applyDarkMode()
  }

  function applyDarkMode() {
    if (darkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // Apply on store init
  applyDarkMode()

  return {
    // sidebar
    sidebarCollapsed,
    sidebarMobileOpen,
    setSidebarCollapsed,
    toggleSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
    // loading
    loading,
    loadingMessage,
    setLoading,
    startLoading,
    stopLoading,
    // toasts
    toasts,
    addToast,
    removeToast,
    clearToasts,
    toast,
    // dark mode
    darkMode,
    isDark,
    toggleDarkMode
  }
})
