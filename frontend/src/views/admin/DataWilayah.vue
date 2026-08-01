<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()

const tab = ref('kwarcab')
const loading = ref(true)
const errorMessage = ref('')

const kwarcabs = ref([])
const kwarans = ref([])
const gudeps = ref([])

const filterKwarcabId = ref('')
const filterKwaranId = ref('')

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formError = ref('')

const form = reactive({
  nama: '',
  kode_wilayah: '',
  alamat_sekretariat: '',
  ketua: '',
  kwarcab_id: '',
  nomor_gudep: '',
  nama_pangkalan: '',
  jenis_pangkalan: 'sekolah',
  kwaran_id: '',
  pembina_gudep: '',
  alamat: ''
})

const jenisPangkalan = ['sekolah', 'komunitas', 'khusus']

const titleMap = {
  kwarcab: 'Data Kwarcab',
  kwaran: 'Data Kwaran',
  gudep: 'Data Gudep'
}

const filteredKwarans = computed(() =>
  filterKwarcabId.value
    ? kwarans.value.filter((k) => k.kwarcab_id === Number(filterKwarcabId.value))
    : kwarans.value
)

const filteredGudeps = computed(() =>
  filterKwaranId.value
    ? gudeps.value.filter((g) => g.kwaran_id === Number(filterKwaranId.value))
    : gudeps.value
)

onMounted(loadAll)

async function loadAll() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [kc, kr, g] = await Promise.all([
      api.get('/admin/kwarcab'),
      api.get('/admin/kwaran'),
      api.get('/admin/gudep')
    ])
    kwarcabs.value = kc.data
    kwarans.value = kr.data
    gudeps.value = g.data
  } catch (err) {
    if (err.response?.status === 401 || err.response?.status === 403) {
      localStorage.removeItem('token')
      router.push({ name: 'login' })
      return
    }
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data wilayah.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  formError.value = ''
  Object.keys(form).forEach((key) => {
    if (key === 'jenis_pangkalan') form[key] = 'sekolah'
    else form[key] = ''
  })
  if (tab.value === 'kwaran') form.kwarcab_id = filterKwarcabId.value
  if (tab.value === 'gudep') {
    form.kwarcab_id = filterKwarcabId.value
    form.kwaran_id = filterKwaranId.value
  }
  showModal.value = true
}

function openEdit(item) {
  isEdit.value = true
  editingId.value = item.id
  formError.value = ''
  const keys = tab.value === 'kwarcab'
    ? ['nama', 'kode_wilayah', 'alamat_sekretariat', 'ketua']
    : tab.value === 'kwaran'
      ? ['nama', 'kwarcab_id', 'ketua']
      : ['nomor_gudep', 'nama_pangkalan', 'jenis_pangkalan', 'kwaran_id', 'pembina_gudep', 'alamat']
  Object.keys(form).forEach((key) => { form[key] = keys.includes(key) ? item[key] ?? '' : '' })
  if (tab.value === 'gudep') {
    const kwaranItem = kwarans.value.find((k) => k.id === item.kwaran_id)
    form.kwarcab_id = kwaranItem ? kwaranItem.kwarcab_id : ''
  }
  showModal.value = true
}

async function save() {
  formError.value = ''
  saving.value = true
  try {
    let payload
    if (tab.value === 'kwarcab') {
      payload = {
        nama: form.nama,
        kode_wilayah: form.kode_wilayah,
        alamat_sekretariat: form.alamat_sekretariat || null,
        ketua: form.ketua || null
      }
      if (isEdit.value) {
        await api.put(`/admin/kwarcab/${editingId.value}`, payload)
      } else {
        await api.post('/admin/kwarcab', payload)
      }
    } else if (tab.value === 'kwaran') {
      payload = {
        nama: form.nama,
        kwarcab_id: Number(form.kwarcab_id),
        ketua: form.ketua || null
      }
      if (isEdit.value) {
        await api.put(`/admin/kwaran/${editingId.value}`, payload)
      } else {
        await api.post('/admin/kwaran', payload)
      }
    } else {
      payload = {
        nomor_gudep: form.nomor_gudep,
        nama_pangkalan: form.nama_pangkalan,
        jenis_pangkalan: form.jenis_pangkalan,
        kwaran_id: Number(form.kwaran_id),
        pembina_gudep: form.pembina_gudep || null,
        alamat: form.alamat || null
      }
      if (isEdit.value) {
        await api.put(`/admin/gudep/${editingId.value}`, payload)
      } else {
        await api.post('/admin/gudep', payload)
      }
    }
    showModal.value = false
    await loadAll()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan data.'
  } finally {
    saving.value = false
  }
}

async function remove(item) {
  const label = item.nama_pangkalan || item.nama
  if (!window.confirm(`Hapus "${label}"? Relasi di bawahnya juga akan dicek.`)) return
  try {
    const endpoint = tab.value === 'kwarcab'
      ? `/admin/kwarcab/${item.id}`
      : tab.value === 'kwaran'
        ? `/admin/kwaran/${item.id}`
        : `/admin/gudep/${item.id}`
    await api.delete(endpoint)
    await loadAll()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus data.')
  }
}

function setTab(name) {
  tab.value = name
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Data Wilayah Keanggotaan</h2>
        <p class="greeting">Kelola hierarki Kwarcab &rarr; Kwaran &rarr; Gudep.</p>
      </div>
    </div>

    <div class="tabs">
      <button
        v-for="(label, key) in titleMap"
        :key="key"
        class="tab"
        :class="{ active: tab === key }"
        @click="setTab(key)"
      >
        {{ label }}
      </button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <template v-if="!loading">
      <!-- TAB K W A R C A B -->
      <div v-if="tab === 'kwarcab'" class="table-card">
        <div class="table-header-row">
          <span>Daftar Kwarcab ({{ kwarcabs.length }})</span>
          <button class="btn-primary btn-add" @click="openCreate">+ Tambah Kwarcab</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Kode</th>
              <th>Nama</th>
              <th>Alamat Sekretariat</th>
              <th>Ketua</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in kwarcabs" :key="item.id">
              <td>{{ item.kode_wilayah }}</td>
              <td>{{ item.nama }}</td>
              <td>{{ item.alamat_sekretariat || '-' }}</td>
              <td>{{ item.ketua || '-' }}</td>
              <td>
                <button class="btn-small" @click="openEdit(item)">Edit</button>
                <button class="btn-small btn-danger" @click="remove(item)">Hapus</button>
              </td>
            </tr>
            <tr v-if="kwarcabs.length === 0">
              <td colspan="5" class="empty-row">Belum ada data Kwarcab.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TAB K W A R A N -->
      <div v-else-if="tab === 'kwaran'" class="table-card">
        <div class="table-header-row">
          <span>Daftar Kwaran</span>
          <button class="btn-primary btn-add" @click="openCreate">+ Tambah Kwaran</button>
        </div>

        <div class="filter-row">
          <label class="filter-label" for="filter-kwaran-kwarcab">Kwarcab:</label>
          <select id="filter-kwaran-kwarcab" v-model="filterKwarcabId">
            <option value="">Semua Kwarcab</option>
            <option v-for="k in kwarcabs" :key="k.id" :value="k.id">{{ k.nama }}</option>
          </select>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>Nama</th>
              <th>Kwarcab</th>
              <th>Ketua</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredKwarans" :key="item.id">
              <td>{{ item.nama }}</td>
              <td>{{ item.kwarcab_nama }}</td>
              <td>{{ item.ketua || '-' }}</td>
              <td>
                <button class="btn-small" @click="openEdit(item)">Edit</button>
                <button class="btn-small btn-danger" @click="remove(item)">Hapus</button>
              </td>
            </tr>
            <tr v-if="filteredKwarans.length === 0">
              <td colspan="4" class="empty-row">Belum ada data Kwaran.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- TAB G U D E P -->
      <div v-else class="table-card">
        <div class="table-header-row">
          <span>Daftar Gudep</span>
          <button class="btn-primary btn-add" @click="openCreate">+ Tambah Gudep</button>
        </div>

        <div class="filter-row">
          <label class="filter-label" for="filter-gudep-kwarcab">Kwarcab:</label>
          <select id="filter-gudep-kwarcab" v-model="filterKwarcabId">
            <option value="">Semua Kwarcab</option>
            <option v-for="k in kwarcabs" :key="k.id" :value="k.id">{{ k.nama }}</option>
          </select>
          <label class="filter-label" for="filter-gudep-kwaran">Kwaran:</label>
          <select id="filter-gudep-kwaran" v-model="filterKwaranId">
            <option value="">Semua Kwaran</option>
            <option v-for="k in filteredKwarans" :key="k.id" :value="k.id">{{ k.nama }}</option>
          </select>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th>Nomor</th>
              <th>Nama Pangkalan</th>
              <th>Jenis</th>
              <th>Kwaran</th>
              <th>Pembina</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredGudeps" :key="item.id">
              <td>{{ item.nomor_gudep }}</td>
              <td>{{ item.nama_pangkalan }}</td>
              <td>{{ item.jenis_pangkalan }}</td>
              <td>{{ item.kwaran_nama }}</td>
              <td>{{ item.pembina_gudep || '-' }}</td>
              <td>
                <button class="btn-small" @click="openEdit(item)">Edit</button>
                <button class="btn-small btn-danger" @click="remove(item)">Hapus</button>
              </td>
            </tr>
            <tr v-if="filteredGudeps.length === 0">
              <td colspan="6" class="empty-row">Belum ada data Gudep.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <form class="modal-card" @submit.prevent="save">
        <h3>{{ isEdit ? 'Edit' : 'Tambah' }} {{ titleMap[tab] }}</h3>

        <div v-if="formError" class="alert-error">{{ formError }}</div>

        <template v-if="tab === 'kwarcab'">
          <div class="form-group">
            <label for="f-kode">Kode Wilayah (KD)</label>
            <input id="f-kode" v-model="form.kode_wilayah" type="text" required />
          </div>
          <div class="form-group">
            <label for="f-nama">Nama Kwarcab</label>
            <input id="f-nama" v-model="form.nama" type="text" required />
          </div>
          <div class="form-group">
            <label for="f-sekret">Alamat Sekretariat</label>
            <textarea id="f-sekret" v-model="form.alamat_sekretariat" rows="2"></textarea>
          </div>
          <div class="form-group">
            <label for="f-ketua">Ketua Kwarcab</label>
            <input id="f-ketua" v-model="form.ketua" type="text" />
          </div>
        </template>

        <template v-else-if="tab === 'kwaran'">
          <div class="form-group">
            <label for="f-nama-kwaran">Nama Kwaran</label>
            <input id="f-nama-kwaran" v-model="form.nama" type="text" required />
          </div>
          <div class="form-group">
            <label for="f-kwarcab-kwaran">Kwarcab</label>
            <select id="f-kwarcab-kwaran" v-model="form.kwarcab_id" required>
              <option value="" disabled>Pilih Kwarcab</option>
              <option v-for="k in kwarcabs" :key="k.id" :value="k.id">{{ k.nama }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="f-ketua-kwaran">Ketua Kwaran</label>
            <input id="f-ketua-kwaran" v-model="form.ketua" type="text" />
          </div>
        </template>

        <template v-else>
          <div class="form-group">
            <label for="f-nomor">Nomor Gudep (kode kwarcab.nomor)</label>
            <input id="f-nomor" v-model="form.nomor_gudep" type="text" required />
          </div>
          <div class="form-group">
            <label for="f-pangkalan">Nama Pangkalan</label>
            <input id="f-pangkalan" v-model="form.nama_pangkalan" type="text" required />
          </div>
          <div class="form-group">
            <label for="f-jenis">Jenis Pangkalan</label>
            <select id="f-jenis" v-model="form.jenis_pangkalan">
              <option v-for="j in jenisPangkalan" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="f-kwarcab-gudep">Kwarcab</label>
            <select id="f-kwarcab-gudep" v-model="form.kwarcab_id" required @change="form.kwaran_id = ''">
              <option value="" disabled>Pilih Kwarcab</option>
              <option v-for="k in kwarcabs" :key="k.id" :value="k.id">{{ k.nama }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="f-kwaran-gudep">Kwaran</label>
            <select id="f-kwaran-gudep" v-model="form.kwaran_id" required>
              <option value="" disabled>Pilih Kwaran</option>
              <option
                v-for="k in kwarans.filter((x) => x.kwarcab_id === Number(form.kwarcab_id))"
                :key="k.id"
                :value="k.id"
              >
                {{ k.nama }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="f-pembina">Pembina Gudep</label>
            <input id="f-pembina" v-model="form.pembina_gudep" type="text" />
          </div>
          <div class="form-group">
            <label for="f-alamat-gudep">Alamat</label>
            <textarea id="f-alamat-gudep" v-model="form.alamat" rows="2"></textarea>
          </div>
        </template>

        <div class="modal-actions">
          <button type="button" class="btn-small" @click="showModal = false">Batal</button>
          <button type="submit" class="btn-submit modal-submit" :disabled="saving">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
