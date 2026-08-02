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
const form = ref({ username: '', nama_lengkap: '', password: '', role: 'staff', is_active: true, tingkat_wilayah: 'kwaran', wilayah_id: '', anggota_id: '' })
const formError = ref('')
const saving = ref(false)

const roles = ['admin', 'staff', 'kontributor', 'penjual']

const kwarcabs = ref([])
const kwarans = ref([])
const gudeps = ref([])

const tingkatLabels = { kwarcab: 'Kwarcab', kwaran: 'Kwaran', gudep: 'Gugus Depan' }

onMounted(async () => {
  await loadUsers()
  await loadWilayah()
})

async function loadWilayah() {
  try {
    const [kc, kr, g] = await Promise.all([
      api.get('/admin/kwarcab'),
      api.get('/admin/kwaran'),
      api.get('/admin/gudep')
    ])
    kwarcabs.value = kc.data
    kwarans.value = kr.data
    gudeps.value = g.data
  } catch {
    // options optional
  }
}

function wilayahOptions() {
  if (form.value.tingkat_wilayah === 'kwarcab') return kwarcabs.value
  if (form.value.tingkat_wilayah === 'kwaran') return kwarans.value
  return gudeps.value
}

function wilayahName(obj) {
  if (!obj) return ''
  return obj.nama_pangkalan || obj.nama || ''
}

function userWilayah(user) {
  if (!user.tingkat_wilayah) return '-'
  const list = user.tingkat_wilayah === 'kwarcab' ? kwarcabs.value
    : user.tingkat_wilayah === 'kwaran' ? kwarans.value : gudeps.value
  const found = list.find((w) => w.id === user.wilayah_id)
  return `${tingkatLabels[user.tingkat_wilayah]} ${wilayahName(found)}`
}

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
  form.value = { username: '', nama_lengkap: '', password: '', role: 'staff', is_active: true, tingkat_wilayah: 'kwaran', wilayah_id: '', anggota_id: '' }
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
    is_active: user.is_active,
    tingkat_wilayah: user.tingkat_wilayah || 'kwaran',
    wilayah_id: user.wilayah_id || '',
    anggota_id: user.anggota_id || ''
  }
  formError.value = ''
  showModal.value = true
}

async function saveUser() {
  formError.value = ''
  saving.value = true
  try {
    const payload = { ...form.value }
    if (payload.role !== 'kontributor') {
      payload.tingkat_wilayah = null
      payload.wilayah_id = null
    } else if (!payload.wilayah_id) {
      formError.value = 'Wilayah wajib dipilih untuk user kontributor.'
      saving.value = false
      return
    }
    if (payload.role === 'penjual') {
      if (!payload.anggota_id) {
        formError.value = 'ID Anggota wajib diisi untuk user penjual.'
        saving.value = false
        return
      }
      payload.anggota_id = parseInt(payload.anggota_id, 10)
    } else {
      payload.anggota_id = null
    }
    if (isEdit.value) {
      await api.put(`/admin/users/${editingId.value}`, payload)
    } else {
      await api.post('/admin/users', payload)
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
  if (role === 'admin') return 'badge badge-admin'
  if (role === 'penjual') return 'badge badge-penjual'
  return 'badge badge-staff'
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
            <th>Wilayah</th>
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
            <td>{{ userWilayah(user) }}</td>
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

        <template v-if="form.role === 'kontributor'">
          <div class="form-group">
            <label for="modal-tingkat">Tingkat Wilayah</label>
            <select id="modal-tingkat" v-model="form.tingkat_wilayah">
              <option value="kwarcab">Kwarcab</option>
              <option value="kwaran">Kwaran</option>
              <option value="gudep">Gugus Depan</option>
            </select>
          </div>

          <div class="form-group">
            <label for="modal-wilayah">Wilayah</label>
            <select id="modal-wilayah" v-model="form.wilayah_id" required>
              <option value="">-- Pilih Wilayah --</option>
              <option
                v-for="w in wilayahOptions()"
                :key="w.id"
                :value="w.id"
              >
                {{ w.nama_pangkalan || w.nama }}
              </option>
            </select>
          </div>
          <p class="form-hint">Kontributor hanya bisa mengirim postingan atas nama wilayah ini.</p>
        </template>

        <template v-if="form.role === 'penjual'">
          <div class="form-group">
            <label for="modal-anggota">ID Anggota (Pemilik Toko)</label>
            <input id="modal-anggota" v-model="form.anggota_id" type="number" required placeholder="contoh: 9" />
          </div>
          <p class="form-hint">Isi ID anggota yang menjadi pemilik toko marketplace.</p>
        </template>

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
