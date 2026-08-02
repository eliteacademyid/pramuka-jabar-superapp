<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Swal from 'sweetalert2'
import api from '../../api/axios'
import BaseCard from '../../components/common/BaseCard.vue'
import BaseButton from '../../components/common/BaseButton.vue'
import BaseInput from '../../components/common/BaseInput.vue'
import BaseSelect from '../../components/common/BaseSelect.vue'
import BaseAlert from '../../components/common/BaseAlert.vue'
import BaseLoading from '../../components/common/BaseLoading.vue'
import BaseModal from '../../components/common/BaseModal.vue'
import BaseBadge from '../../components/common/BaseBadge.vue'

const router = useRouter()

const users = ref([])
const loading = ref(true)
const errorMessage = ref('')

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({ username: '', nama_lengkap: '', password: '', role: 'staff', is_active: true })
const formError = ref('')
const saving = ref(false)

const roles = [{ value: 'admin', label: 'Admin' }, { value: 'staff', label: 'Staff' }]

onMounted(loadUsers)

async function loadUsers() {
  loading.value = true
  errorMessage.value = ''
  try {
    const res = await api.get('/admin/users')
    users.value = res.data
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
      return
    }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data user.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.value = { username: '', nama_lengkap: '', password: '', role: 'staff', is_active: true }
  formError.value = ''
  showModal.value = true
}

function openEdit(user) {
  isEdit.value = true
  editingId.value = user.id
  form.value = {
    username: user.username,
    nama_lengkap: user.nama_lengkap,
    password: '',
    role: user.role,
    is_active: user.is_active
  }
  formError.value = ''
  showModal.value = true
}

async function saveUser() {
  formError.value = ''
  saving.value = true
  try {
    if (isEdit.value) {
      await api.put(`/admin/users/${editingId.value}`, form.value)
    } else {
      await api.post('/admin/users', form.value)
    }
    showModal.value = false
    await loadUsers()
    await Swal.fire({ icon: 'success', title: 'Data user tersimpan', timer: 1600, showConfirmButton: false })
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan user.'
  } finally {
    saving.value = false
  }
}

async function deleteUser(user) {
  const result = await Swal.fire({
    title: `Hapus user ${user.username}?`,
    text: 'Tindakan ini tidak dapat dibatalkan.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc2626',
    cancelButtonColor: '#64748b',
    confirmButtonText: 'Ya, hapus'
  })

  if (!result.isConfirmed) return

  try {
    await api.delete(`/admin/users/${user.id}`)
    await loadUsers()
    await Swal.fire({ icon: 'success', title: 'User dihapus', timer: 1400, showConfirmButton: false })
  } catch (err) {
    await Swal.fire({ icon: 'error', title: err.response?.data?.detail || 'Gagal menghapus user.' })
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.2em] text-pramuka-600">Manajemen Akses</p>
        <h2 class="mt-2 text-2xl font-semibold text-slate-900">Kelola pengguna aplikasi</h2>
        <p class="mt-2 max-w-2xl text-sm text-slate-500">Tambah, ubah, dan nonaktifkan akun pengguna yang dapat mengakses dashboard.</p>
      </div>
      <BaseButton @click="openCreate">+ Tambah User</BaseButton>
    </div>

    <BaseAlert v-if="errorMessage" type="danger">{{ errorMessage }}</BaseAlert>

    <BaseCard title="Daftar User" subtitle="Data akun yang saat ini aktif dalam sistem">
      <div v-if="loading" class="py-4">
        <BaseLoading />
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Username</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Nama Lengkap</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Role</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Status</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="user in users" :key="user.id" class="hover:bg-slate-50">
              <td class="px-4 py-3 text-sm text-slate-700">{{ user.id }}</td>
              <td class="px-4 py-3 text-sm text-slate-700">{{ user.username }}</td>
              <td class="px-4 py-3 text-sm text-slate-700">{{ user.nama_lengkap }}</td>
              <td class="px-4 py-3 text-sm text-slate-700">
                <BaseBadge :variant="user.role === 'admin' ? 'info' : 'success'">{{ user.role }}</BaseBadge>
              </td>
              <td class="px-4 py-3 text-sm text-slate-700">
                <BaseBadge :variant="user.is_active ? 'success' : 'warning'">{{ user.is_active ? 'Aktif' : 'Nonaktif' }}</BaseBadge>
              </td>
              <td class="px-4 py-3 text-sm text-slate-700">
                <div class="flex flex-wrap gap-2">
                  <BaseButton variant="secondary" size="sm" @click="openEdit(user)">Edit</BaseButton>
                  <BaseButton variant="danger" size="sm" @click="deleteUser(user)">Hapus</BaseButton>
                </div>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="6" class="px-4 py-6 text-center text-sm text-slate-500">Belum ada pengguna.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </BaseCard>

    <BaseModal v-model="showModal" :title="isEdit ? 'Edit User' : 'Tambah User'">
      <form class="space-y-4" @submit.prevent="saveUser">
        <BaseAlert v-if="formError" type="danger">{{ formError }}</BaseAlert>
        <BaseInput v-model="form.username" label="Username" placeholder="Masukkan username" />
        <BaseInput v-model="form.nama_lengkap" label="Nama Lengkap" placeholder="Masukkan nama lengkap" />
        <BaseInput v-model="form.password" label="Password" type="password" :placeholder="isEdit ? 'Kosongkan jika tidak diubah' : 'Minimal 6 karakter'" />
        <BaseSelect v-model="form.role" label="Role" :options="roles" placeholder="Pilih role" />
        <label class="flex items-center gap-2 text-sm font-medium text-slate-700">
          <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-pramuka-600 focus:ring-pramuka-500" />
          Status aktif
        </label>
        <div class="flex justify-end gap-3 pt-2">
          <BaseButton type="button" variant="secondary" @click="showModal = false">Batal</BaseButton>
          <BaseButton type="submit" :loading="saving">{{ saving ? 'Menyimpan...' : 'Simpan' }}</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
