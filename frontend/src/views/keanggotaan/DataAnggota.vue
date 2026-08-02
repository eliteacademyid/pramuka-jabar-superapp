<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const loading = ref(true)
const errorMessage = ref('')
const anggotaList = ref([])
const gudeps = ref([])
const wilayahs = ref([])
const selectedJenjang = ref('')

const showModal = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({ nta: '', nama_lengkap: '', tanggal_lahir: '', jenis_kelamin: 'L', jenjang: 'siaga', status_aktif: true, kwarcab: '', kwarran: '', gudep_nama: '' })
const formError = ref('')
const saving = ref(false)

const jenjangOptions = ['siaga', 'penggalang', 'penegak', 'pandega', 'dewasa']
const jenjangLabels = { siaga: 'Siaga', penggalang: 'Penggalang', penegak: 'Penegak', pandega: 'Pandega', dewasa: 'Dewasa' }

onMounted(async () => {
  try {
    const [a, g, w] = await Promise.all([api.get('/anggota/'), api.get('/gudep'), api.get('/wilayah')])
    anggotaList.value = a.data
    gudeps.value = g.data
    wilayahs.value = w.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  } finally {
    loading.value = false
  }
})

const filtered = () => {
  if (!selectedJenjang.value) return anggotaList.value
  return anggotaList.value.filter((a) => a.jenjang === selectedJenjang.value)
}

function gudepNama(id) {
  return gudeps.value.find((g) => g.id === id)?.nama || `Gudep #${id}`
}

function kwarranNama(gudepId) {
  const g = gudeps.value.find((x) => x.id === gudepId)
  if (!g) return '-'
  const wilayah = wilayahs.value.find((w) => w.id === g.wilayah_id)
  if (!wilayah || wilayah.tingkat !== 'Kwartir Ranting') return '-'
  return wilayah.nama
}

function kwarcabNama(gudepId) {
  const g = gudeps.value.find((x) => x.id === gudepId)
  if (!g) return '-'
  const wilayah = wilayahs.value.find((w) => w.id === g.wilayah_id)
  if (!wilayah) return '-'
  if (wilayah.tingkat === 'Kwartir Cabang') return wilayah.nama
  const cabang = wilayahs.value.find((w) => w.id === wilayah.parent_id)
  return cabang ? cabang.nama : '-'
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.value = { nta: '', nama_lengkap: '', tanggal_lahir: '', jenis_kelamin: 'L', jenjang: 'siaga', status_aktif: true, kwarcab: '', kwarran: '', gudep_nama: '' }
  formError.value = ''
  showModal.value = true
}

function openEdit(a) {
  isEdit.value = true
  editingId.value = a.id
  form.value = {
    nta: a.nta,
    nama_lengkap: a.nama_lengkap,
    tanggal_lahir: a.tanggal_lahir.slice(0, 10),
    jenis_kelamin: a.jenis_kelamin,
    jenjang: a.jenjang,
    status_aktif: a.status_aktif,
    kwarcab: kwarcabNama(a.gudep_id),
    kwarran: kwarranNama(a.gudep_id),
    gudep_nama: gudepNama(a.gudep_id)
  }
  formError.value = ''
  showModal.value = true
}

async function resolveWilayah(nama, tingkat, parentId) {
  const trimmed = (nama || '').trim()
  if (!trimmed) throw new Error(`${tingkat} wajib diisi`)
  const found = wilayahs.value.find(
    (w) => w.nama.toLowerCase() === trimmed.toLowerCase() && w.tingkat === tingkat
  )
  if (found) return found.id
  const res = await api.post('/wilayah', { nama: trimmed, tingkat, parent_id: parentId })
  wilayahs.value.push(res.data)
  return res.data.id
}

async function resolveGudep(nama, kwarranId) {
  const trimmed = (nama || '').trim()
  if (!trimmed) throw new Error('Gudep wajib diisi')
  const found = gudeps.value.find((g) => g.nama.toLowerCase() === trimmed.toLowerCase())
  if (found) return found.id
  const res = await api.post('/gudep', { nama: trimmed, wilayah_id: kwarranId })
  gudeps.value.push(res.data)
  return res.data.id
}

async function saveAnggota() {
  formError.value = ''
  saving.value = true
  try {
    const daerah = wilayahs.value.find((w) => w.tingkat === 'Daerah')
    const kwarcabId = await resolveWilayah(form.value.kwarcab, 'Kwartir Cabang', daerah?.id || null)
    const kwarranId = await resolveWilayah(form.value.kwarran, 'Kwartir Ranting', kwarcabId)
    const gudepId = await resolveGudep(form.value.gudep_nama, kwarranId)
    const payload = {
      nta: form.value.nta,
      nama_lengkap: form.value.nama_lengkap,
      tanggal_lahir: new Date(form.value.tanggal_lahir).toISOString(),
      jenis_kelamin: form.value.jenis_kelamin,
      jenjang: form.value.jenjang,
      status_aktif: form.value.status_aktif,
      gudep_id: gudepId
    }
    if (isEdit.value) {
      await api.put(`/anggota/${editingId.value}`, payload)
    } else {
      await api.post('/anggota/', payload)
    }
    showModal.value = false
    const a = await api.get('/anggota/')
    anggotaList.value = a.data
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan anggota.'
  } finally {
    saving.value = false
  }
}

async function deleteAnggota(a) {
  if (!window.confirm(`Hapus anggota "${a.nama_lengkap}"?`)) return
  try {
    await api.delete(`/anggota/${a.id}`)
    const res = await api.get('/anggota/')
    anggotaList.value = res.data
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menghapus anggota.')
  }
}

function formatTanggal(iso) {
  return new Date(iso).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<template>
  <div class="dashboard-content">
    <div class="page-header">
      <div>
        <h2>Data Anggota</h2>
        <p class="greeting">Kelola data potensi keanggotaan per jenjang.</p>
      </div>
      <button class="btn-primary btn-add" @click="openCreate">+ Tambah Anggota</button>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div class="filter-bar">
      <button
        v-for="j in ['', ...jenjangOptions]"
        :key="j"
        class="btn-small"
        :class="{ 'active-filter': selectedJenjang === j }"
        @click="selectedJenjang = j"
      >
        {{ j ? jenjangLabels[j] : 'Semua' }}
      </button>
    </div>

    <div class="table-card" v-if="!loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>NTA</th>
            <th>Nama Lengkap</th>
            <th>Jenjang</th>
            <th>Jenis Kelamin</th>
            <th>Kwarcab</th>
            <th>Kwarran</th>
            <th>Gudep</th>
            <th>Status</th>
            <th>Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in filtered()" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.nta }}</td>
            <td>{{ a.nama_lengkap }}</td>
            <td>{{ jenjangLabels[a.jenjang] || a.jenjang }}</td>
            <td>{{ a.jenis_kelamin === 'L' ? 'Laki-laki' : 'Perempuan' }}</td>
            <td>{{ kwarcabNama(a.gudep_id) }}</td>
            <td>{{ kwarranNama(a.gudep_id) }}</td>
            <td>{{ gudepNama(a.gudep_id) }}</td>
            <td>
              <span :class="a.status_aktif ? 'status status-active' : 'status status-inactive'">
                {{ a.status_aktif ? 'Aktif' : 'Nonaktif' }}
              </span>
            </td>
            <td>
              <button class="btn-small" @click="openEdit(a)">Edit</button>
              <button class="btn-small btn-danger" @click="deleteAnggota(a)">Hapus</button>
            </td>
          </tr>
          <tr v-if="filtered().length === 0">
            <td colspan="10" class="empty-row">Belum ada data anggota.</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else class="greeting">Memuat data...</p>

    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <form class="modal-card modal-wide" @submit.prevent="saveAnggota">
        <h3>{{ isEdit ? 'Edit Anggota' : 'Tambah Anggota' }}</h3>

        <div v-if="formError" class="alert-error">{{ formError }}</div>

        <div class="form-group">
          <label for="m-nta">NTA</label>
          <input id="m-nta" v-model="form.nta" type="text" required />
        </div>
        <div class="form-group">
          <label for="m-nama">Nama Lengkap</label>
          <input id="m-nama" v-model="form.nama_lengkap" type="text" required />
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label for="m-tgl">Tanggal Lahir</label>
            <input id="m-tgl" v-model="form.tanggal_lahir" type="date" required />
          </div>
          <div class="form-group">
            <label for="m-jk">Jenis Kelamin</label>
            <select id="m-jk" v-model="form.jenis_kelamin">
              <option value="L">Laki-laki</option>
              <option value="P">Perempuan</option>
            </select>
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label for="m-jenjang">Jenjang</label>
            <select id="m-jenjang" v-model="form.jenjang">
              <option v-for="j in jenjangOptions" :key="j" :value="j">{{ jenjangLabels[j] }}</option>
            </select>
          </div>
          <div class="form-group">
            <label for="m-kwarcab">Kwarcab (Kwartir Cabang)</label>
            <input
              id="m-kwarcab"
              v-model="form.kwarcab"
              type="text"
              placeholder="Contoh: Kota Bandung"
              required
            />
          </div>
          <div class="form-group">
            <label for="m-kwarran">Kwarran (Kwartir Ranting)</label>
            <input
              id="m-kwarran"
              v-model="form.kwarran"
              type="text"
              placeholder="Contoh: Ranting Cibeunying"
              required
            />
          </div>
          <div class="form-group">
            <label for="m-gudep">Gudep</label>
            <input
              id="m-gudep"
              v-model="form.gudep_nama"
              type="text"
              placeholder="Contoh: Gudep 01"
              required
            />
          </div>
        </div>
        <div class="form-group checkbox-group">
          <label>
            <input v-model="form.status_aktif" type="checkbox" />
            Status aktif
          </label>
        </div>

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

<style scoped>
.filter-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.active-filter {
  background: var(--brown);
  color: var(--white);
}

.modal-wide {
  max-width: 520px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
</style>
