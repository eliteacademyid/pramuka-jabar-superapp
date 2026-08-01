<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

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

const roles = ['admin', 'staff']

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
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan user.'
  } finally {
    saving.value = false
  }
}

async function deleteUser(user) {
  if (!window.confirm(`Hapus user "${user.username}"?`)) return
  try {
    await api.delete(`/admin/users/${user.id}`)
    await loadUsers()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus user.')
  }
}

function roleBadgeClass(role) {
  return role === 'admin' ? 'badge badge-admin' : 'badge badge-staff'
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Manajemen User</h2>
        <p class="greeting">Kelola akun pengguna aplikasi.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Tambah User</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Nama Lengkap</th>
            <th>Role</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.nama_lengkap }}</td>
            <td>
              <span :class="roleBadgeClass(user.role)">{{ user.role }}</span>
            </td>
            <td>
              <span :class="user.is_active ? 'status status-active' : 'status status-inactive'">
                {{ user.is_active ? 'Aktif' : 'Nonaktif' }}
              </span>
            </td>
            <td>
              <button class="btn-small" @click="openEdit(user)">Edit</button>
              <button class="btn-small btn-danger" @click="deleteUser(user)">
                Hapus
              </button>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="6" class="empty-row">Belum ada pengguna.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <form class="modal-card" @submit.prevent="saveUser">
        <h3>{{ isEdit ? 'Edit User' : 'Tambah User' }}</h3>

        <div v-if="formError" class="alert-error">{{ formError }}</div>

        <div class="form-group">
          <label for="modal-username">Username</label>
          <input id="modal-username" v-model="form.username" type="text" required />
        </div>

        <div class="form-group">
          <label for="modal-nama">Nama Lengkap</label>
          <input id="modal-nama" v-model="form.nama_lengkap" type="text" required />
        </div>

        <div class="form-group">
          <label for="modal-password">
            Password {{ isEdit ? '(kosongkan jika tidak diubah)' : '(minimal 6 karakter)' }}
          </label>
          <input
            id="modal-password"
            v-model="form.password"
            type="password"
            :required="!isEdit"
          />
        </div>

        <div class="form-group">
          <label for="modal-role">Role</label>
          <select id="modal-role" v-model="form.role">
            <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
          </select>
        </div>

        <div class="form-group checkbox-group">
          <label>
            <input v-model="form.is_active" type="checkbox" />
            Status aktif
          </label>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-small" @click="showModal = false">
            Batal
          </button>
          <button type="submit" class="btn-submit modal-submit" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
