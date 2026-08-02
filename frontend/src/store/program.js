import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getPrograms, getProgram, createProgram, updateProgram, deleteProgram } from '../services/programService'

export const useProgramStore = defineStore('program', () => {
  const programs = ref([])
  const currentProgram = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function fetchPrograms(params = {}) {
    loading.value = true
    error.value = ''
    try {
      const res = await getPrograms(params)
      programs.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal memuat program.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchProgramById(id) {
    loading.value = true
    error.value = ''
    try {
      const res = await getProgram(id)
      currentProgram.value = res.data
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal memuat detail program.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addProgram(payload) {
    loading.value = true
    error.value = ''
    try {
      const res = await createProgram(payload)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal membuat program.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function editProgram(id, payload) {
    loading.value = true
    error.value = ''
    try {
      const res = await updateProgram(id, payload)
      return res.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal memperbarui program.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function removeProgram(id) {
    loading.value = true
    error.value = ''
    try {
      await deleteProgram(id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal menghapus program.'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    programs,
    currentProgram,
    loading,
    error,
    fetchPrograms,
    fetchProgramById,
    addProgram,
    editProgram,
    removeProgram
  }
})
