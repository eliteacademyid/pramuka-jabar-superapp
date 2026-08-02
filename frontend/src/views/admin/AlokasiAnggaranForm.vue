<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const editId = route.query.edit ? Number(route.query.edit) : null

const programList = ref([])
const allAlokasi = ref([])
const form = reactive({
  program_kerja_id: '',
  tahun_anggaran: new Date().getFullYear(),
  jumlah_anggaran: '',
  sumber_dana: 'APBD',
  catatan: ''
})

const sumberOptions = ['APBD', 'Swadaya', 'Bantuan Pusat', 'Lainnya']

const errorMessage = ref('')
const saving = ref(false)

const programTersedia = computed(() => {
  const tahun = Number(form.tahun_anggaran)
  const sudahDialokasi = allAlokasi.value
    .filter((a) => a.tahun_anggaran === tahun)
    .map((a) => a.program_kerja_id)
  return programList.value.filter((p) => !sudahDialokasi.includes(p.id))
})

onMounted(async () => {
  try {
    const [prog, alok] = await Promise.all([
      api.get('/admin/program-kerja'),
      api.get('/admin/anggaran-program')
    ])
    programList.value = prog.data
    allAlokasi.value = alok.data
    if (editId) {
      const target = alok.data.find((a) => a.id === editId)
      if (target) {
        form.program_kerja_id = target.program_kerja_id
        form.tahun_anggaran = target.tahun_anggaran
        form.jumlah_anggaran = target.jumlah_anggaran
        form.sumber_dana = target.sumber_dana
        form.catatan = target.catatan || ''
      }
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat data.'
  }
})

async function handleSubmit() {
  errorMessage.value = ''
  if (!form.program_kerja_id || !form.jumlah_anggaran || Number(form.jumlah_anggaran) <= 0) {
    errorMessage.value = 'Program kerja dan jumlah anggaran (lebih dari 0) wajib diisi.'
    return
  }
  saving.value = true
  try {
    const payload = {
      program_kerja_id: Number(form.program_kerja_id),
      tahun_anggaran: Number(form.tahun_anggaran),
      jumlah_anggaran: Number(form.jumlah_anggaran),
      sumber_dana: form.sumber_dana,
      catatan: form.catatan || null
    }
    if (editId) {
      await api.put(`/admin/anggaran-program/${editId}`, payload)
      router.push({ name: 'admin-anggaran-alokasi' })
    } else {
      const res = await api.post('/admin/anggaran-program', payload)
      router.push({ name: 'admin-anggaran-realisasi', params: { id: res.data.id } })
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan alokasi anggaran.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <router-link to="/admin/anggaran-alokasi" class="back-link">Kembali ke Alokasi Anggaran</router-link>

    <div class="page-header">
      <div>
        <h2>{{ editId ? 'Edit Alokasi Anggaran' : 'Alokasikan Anggaran Baru' }}</h2>
        <p class="greeting">Satu program kerja hanya boleh punya satu alokasi per tahun anggaran.</p>
      </div>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <form class="table-card" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Tahun Anggaran</label>
        <input v-model.number="form.tahun_anggaran" type="number" min="2000" max="2100" required />
      </div>

      <div class="form-group">
        <label>Program Kerja</label>
        <select v-model="form.program_kerja_id" required>
          <option value="">-- Pilih Program Kerja --</option>
          <template v-if="!editId">
            <option v-for="p in programTersedia" :key="p.id" :value="p.id">
              {{ p.judul }} ({{ p.nama_bidang }})
            </option>
          </template>
          <template v-else>
            <option v-for="p in programList" :key="p.id" :value="p.id">
              {{ p.judul }} ({{ p.nama_bidang }})
            </option>
          </template>
        </select>
        <p v-if="!editId && !programTersedia.length" class="form-hint">
          Semua program kerja sudah punya alokasi untuk tahun {{ form.tahun_anggaran }}.
        </p>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Jumlah Anggaran (Rp)</label>
          <input v-model.number="form.jumlah_anggaran" type="number" min="1" placeholder="contoh: 150000000" required />
        </div>
        <div class="form-group">
          <label>Sumber Dana</label>
          <select v-model="form.sumber_dana">
            <option v-for="s in sumberOptions" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Catatan</label>
        <textarea v-model="form.catatan" rows="3" placeholder="Catatan alokasi (opsional)"></textarea>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn-small" @click="router.push({ name: 'admin-anggaran-alokasi' })">Batal</button>
        <button type="submit" class="btn-submit modal-submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : editId ? 'Simpan Perubahan' : 'Simpan Alokasi' }}
        </button>
      </div>
    </form>
  </div>
</template>
