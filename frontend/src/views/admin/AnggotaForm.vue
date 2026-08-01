<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  initial: { type: Object, default: null },
  isEdit: { type: Boolean, default: false },
  kwarcabs: { type: Array, default: () => [] },
  kwarans: { type: Array, default: () => [] },
  gudeps: { type: Array, default: () => [] },
  save: { type: Function, required: true }
})

const emit = defineEmits(['saved', 'cancel'])

const golonganList = ['siaga', 'penggalang', 'penegak', 'pandega', 'dewasa']
const jabatanList = ['Pembina Pramuka', 'Pelatih', 'Andalan', 'Lainnya']
const jkList = ['L', 'P']

const saving = ref(false)
const formError = ref('')

const form = reactive({
  nis_anggota: '',
  nama_lengkap: '',
  jenis_kelamin: 'L',
  tempat_lahir: '',
  tanggal_lahir: '',
  golongan: 'penggalang',
  jabatan_dewasa: '',
  kwarcab_id: '',
  kwaran_id: '',
  gudep_id: '',
  nomor_hp: '',
  status_aktif: true,
  tanggal_bergabung: ''
})

watch(
  () => props.initial,
  (val) => {
    Object.assign(form, {
      nis_anggota: val?.nis_anggota ?? '',
      nama_lengkap: val?.nama_lengkap ?? '',
      jenis_kelamin: val?.jenis_kelamin ?? 'L',
      tempat_lahir: val?.tempat_lahir ?? '',
      tanggal_lahir: val?.tanggal_lahir ?? '',
      golongan: val?.golongan ?? 'penggalang',
      jabatan_dewasa: val?.jabatan_dewasa ?? '',
      kwarcab_id: val ? findGudepKwarcab(val.gudep_id) : '',
      kwaran_id: val ? findGudepKwaran(val.gudep_id) : '',
      gudep_id: val?.gudep_id ?? '',
      nomor_hp: val?.nomor_hp ?? '',
      status_aktif: val?.status_aktif ?? true,
      tanggal_bergabung: val?.tanggal_bergabung ?? ''
    })
    formError.value = ''
  },
  { immediate: true }
)

function findGudepKwaran(gudepId) {
  const g = props.gudeps.find((x) => x.id === gudepId)
  return g ? g.kwaran_id : ''
}

function findGudepKwarcab(gudepId) {
  const g = props.gudeps.find((x) => x.id === gudepId)
  if (!g) return ''
  const k = props.kwarans.find((x) => x.id === g.kwaran_id)
  return k ? k.kwarcab_id : ''
}

const filteredKwarans = computed(() =>
  props.kwarans.filter((k) => k.kwarcab_id === Number(form.kwarcab_id))
)

const filteredGudeps = computed(() => {
  const base = props.gudeps.filter((g) => g.kwaran_id === Number(form.kwaran_id))
  return base.map((g) => ({
    id: g.id,
    label: `${g.nomor_gudep} - ${g.nama_pangkalan}`
  }))
})

watch(
  () => form.kwarcab_id,
  () => {
    form.kwaran_id = ''
    form.gudep_id = ''
  }
)

watch(
  () => form.kwaran_id,
  () => {
    form.gudep_id = ''
  }
)

function validate() {
  if (!form.nis_anggota.trim()) return 'NIS wajib diisi.'
  if (!form.nama_lengkap.trim()) return 'Nama lengkap wajib diisi.'
  if (!form.gudep_id) return 'Pilih Gudep.'
  if (form.golongan === 'dewasa' && !form.jabatan_dewasa) {
    return 'Jabatan wajib diisi untuk golongan Dewasa.'
  }
  if (form.tanggal_lahir && new Date(form.tanggal_lahir) > new Date()) {
    return 'Tanggal lahir tidak boleh di masa depan.'
  }
  if (form.tanggal_bergabung && new Date(form.tanggal_bergabung) > new Date()) {
    return 'Tanggal bergabung tidak boleh di masa depan.'
  }
  return ''
}

async function submit() {
  formError.value = ''
  const err = validate()
  if (err) {
    formError.value = err
    return
  }
  saving.value = true
  try {
    const payload = {
      nis_anggota: form.nis_anggota.trim(),
      nama_lengkap: form.nama_lengkap.trim(),
      jenis_kelamin: form.jenis_kelamin,
      tempat_lahir: form.tempat_lahir || null,
      tanggal_lahir: form.tanggal_lahir || null,
      golongan: form.golongan,
      jabatan_dewasa: form.golongan === 'dewasa' ? form.jabatan_dewasa : null,
      gudep_id: Number(form.gudep_id),
      nomor_hp: form.nomor_hp || null,
      status_aktif: form.status_aktif,
      tanggal_bergabung: form.tanggal_bergabung || null,
      foto_url: null
    }
    await props.save(payload)
    emit('saved')
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Gagal menyimpan data.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <form class="modal-card anggota-form" @submit.prevent="submit">
    <h3>{{ isEdit ? 'Edit Anggota' : 'Tambah Anggota' }}</h3>

    <div v-if="formError" class="alert-error">{{ formError }}</div>

    <div class="form-grid">
      <div class="form-group">
        <label for="af-nis">NIS Anggota</label>
        <input id="af-nis" v-model="form.nis_anggota" type="text" required />
      </div>
      <div class="form-group">
        <label for="af-nama">Nama Lengkap</label>
        <input id="af-nama" v-model="form.nama_lengkap" type="text" required />
      </div>
      <div class="form-group">
        <label for="af-jk">Jenis Kelamin</label>
        <select id="af-jk" v-model="form.jenis_kelamin">
          <option v-for="jk in jkList" :key="jk" :value="jk">
            {{ jk === 'L' ? 'Laki-laki' : 'Perempuan' }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="af-tmplahir">Tempat Lahir</label>
        <input id="af-tmplahir" v-model="form.tempat_lahir" type="text" />
      </div>
      <div class="form-group">
        <label for="af-tgllahir">Tanggal Lahir</label>
        <input id="af-tgllahir" v-model="form.tanggal_lahir" type="date" />
      </div>
      <div class="form-group">
        <label for="af-tglgabung">Tanggal Bergabung</label>
        <input id="af-tglgabung" v-model="form.tanggal_bergabung" type="date" />
      </div>
      <div class="form-group">
        <label for="af-golongan">Golongan</label>
        <select id="af-golongan" v-model="form.golongan">
          <option v-for="g in golonganList" :key="g" :value="g">{{ g }}</option>
        </select>
      </div>
      <div v-if="form.golongan === 'dewasa'" class="form-group">
        <label for="af-jabatan">Jabatan (Dewasa)</label>
        <select id="af-jabatan" v-model="form.jabatan_dewasa">
          <option value="" disabled>Pilih jabatan</option>
          <option v-for="j in jabatanList" :key="j" :value="j">{{ j }}</option>
        </select>
      </div>
      <div class="form-group">
        <label for="af-nohp">Nomor HP</label>
        <input id="af-nohp" v-model="form.nomor_hp" type="text" />
      </div>
    </div>

    <div class="form-group">
      <label for="af-kwarcab">Kwarcab</label>
      <select id="af-kwarcab" v-model="form.kwarcab_id">
        <option value="" disabled>Pilih Kwarcab</option>
        <option v-for="k in kwarcabs" :key="k.id" :value="k.id">{{ k.nama }}</option>
      </select>
    </div>
    <div class="form-group">
      <label for="af-kwaran">Kwaran</label>
      <select id="af-kwaran" v-model="form.kwaran_id" :disabled="!form.kwarcab_id">
        <option value="" disabled>Pilih Kwaran</option>
        <option v-for="k in filteredKwarans" :key="k.id" :value="k.id">{{ k.nama }}</option>
      </select>
    </div>
    <div class="form-group">
      <label for="af-gudep">Gudep</label>
      <select id="af-gudep" v-model="form.gudep_id" :disabled="!form.kwaran_id">
        <option value="" disabled>Pilih Gudep</option>
        <option v-for="g in filteredGudeps" :key="g.id" :value="g.id">{{ g.label }}</option>
      </select>
    </div>

    <div class="form-group checkbox-group">
      <label>
        <input v-model="form.status_aktif" type="checkbox" />
        Status aktif
      </label>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn-small" @click="emit('cancel')">Batal</button>
      <button type="submit" class="btn-submit modal-submit" :disabled="saving">
        {{ saving ? 'Menyimpan...' : 'Simpan' }}
      </button>
    </div>
  </form>
</template>
