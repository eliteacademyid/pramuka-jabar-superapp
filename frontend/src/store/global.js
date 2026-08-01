import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGlobalStore = defineStore('global', () => {
  const sidebarCollapsed = ref(false)
  const loading = ref(false)
  const toast = ref(null)

  function setSidebarCollapsed(value) {
    sidebarCollapsed.value = value
  }

  function setLoading(value) {
    loading.value = value
  }

  function setToast(message, type = 'success') {
    toast.value = { message, type }
  }

  return { sidebarCollapsed, loading, toast, setSidebarCollapsed, setLoading, setToast }
})
