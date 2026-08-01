<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '../../store/auth'
import BaseButton from '../../components/common/BaseButton.vue'
import BaseInput from '../../components/common/BaseInput.vue'
import BaseAlert from '../../components/common/BaseAlert.vue'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMessage = ref('')

async function submitLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    await authStore.login(form.value)
    await Swal.fire({
      title: 'Login berhasil',
      text: 'Anda akan diarahkan ke dashboard.',
      icon: 'success',
      confirmButtonColor: '#3f7d20'
    })
    toast.success('Selamat datang di Pramuka SuperApp')
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = error?.response?.data?.detail || 'Login gagal. Coba cek username dan password.'
    toast.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.08),_transparent_35%),linear-gradient(135deg,_#f8fafc_0%,_#f0fdf4_100%)] px-4 py-10 sm:px-6 lg:px-8">
    <div class="mx-auto flex max-w-6xl flex-col overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-soft lg:flex-row">
      <div class="flex flex-1 flex-col justify-center bg-gradient-to-br from-pramuka-700 via-pramuka-600 to-pramuka-500 p-8 text-white sm:p-10 lg:p-12">
        <div class="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-white/15 text-2xl font-bold">P</div>
        <h1 class="text-3xl font-semibold">Pramuka Kwarda Jabar</h1>
        <p class="mt-3 max-w-md text-sm leading-7 text-pramuka-50">
          Akses dashboard operasional untuk memantau program, kegiatan, anggaran, dan capaian seluruh kegiatan Pramuka Jawa Barat.
        </p>
      </div>

      <div class="flex flex-1 items-center justify-center p-6 sm:p-8 lg:p-10">
        <div class="w-full max-w-md">
          <div class="mb-6 text-center">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-pramuka-600">Masuk ke SuperApp</p>
            <h2 class="mt-2 text-2xl font-semibold text-slate-900">Selamat datang kembali</h2>
            <p class="mt-2 text-sm text-slate-500">Silakan gunakan akun Anda untuk mengakses dashboard.</p>
          </div>

          <BaseAlert v-if="errorMessage" type="danger" class="mb-4">{{ errorMessage }}</BaseAlert>

          <form class="space-y-4" @submit.prevent="submitLogin">
            <BaseInput v-model="form.username" label="Username" placeholder="Masukkan username" />
            <BaseInput v-model="form.password" label="Password" type="password" placeholder="Masukkan password" />
            <BaseButton type="submit" :loading="loading" class="w-full">Masuk</BaseButton>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
