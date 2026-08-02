<script setup>
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  initial: { type: Object, default: null },
  isEdit: { type: Boolean, default: false },
  bidang: { type: Array, default: () => [] },
  save: { type: Function, required: true }
})

const emit = defineEmits(['saved', 'cancel'])

const statusList = ['rencana', 'berjalan', 'selesai', 'dibatalkan']
const years = []

const yearNow = new Date().getFullYear()
for (let y = yearNow + 1; y >= yearNow - 4; y--) {
  years.push(y)
}

const saving = ref(false)
const formError = ref('')

const form = reactive({
  judul: '',
  bidang_id: '',
  tahun: yearNow,
  deskripsi: '',
  target_capaian: '',
  penanggung_jawab: '',
  status: 'rencana'
})

watch(
  () => props.initial,
  (val) => {
    Object.assign(form, {
      judul: val?.judul ?? '',
      bidang_id: val?.bidang_id ?? '',
      tahun: val?.tahun ?? yearNow,
      deskripsi: val?.deskripsi ?? '',
      target_capaian: val?.target_capaian ?? '',
      penanggung_jawab: val?.penanggung_jawab ?? '',
      status: val?.status ?? 'rencana'
    })
    formError.value = ''
  },
  { immediate: true }
)

async function submit() {
  formError.value = ''
  if (!form.judul.trim()) {
    formError.value = 'Judul wajib diisi.'
    return
  }
  if (!form.bidang_id) {
    formError.value = 'Pilih bidang.'
    return
  }
  saving.value = true
  try {
    const payload = {
      judul: form.judul.trim(),
      bidang_id: Number(form.bidang_id),
      tahun: Number(form.tahun),
      deskripsi: form.deskripsi || null,
      target_capaian: form.target_capaian || null,
      penanggung_jawab: form.penanggung_jawab || null,
      status: form.status
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
  <form class="modal-card" @submit.prevent="submit">
    <h3>{{ isEdit ? 'Edit Program Kerja' : 'Tambah Program Kerja' }}</h3>

    <div v-if="formError" class="alert-error">{{ formError }}</div>

    <div class="form-group">
      <label for="pk-judul">Judul Program Kerja</label>
      <input id="pk-judul" v-model="form.judul" type="text" required />
    </div>

    <div class="form-group">
      <label for="pk-bidang">Bidang Kwarda</label>
      <select id="pk-bidang" v-model="form.bidang_id" required>
        <option value="" disabled>Pilih bidang</option>
        <option v-for="b in bidang" :key="b.id" :value="b.id">{{ b.nama_bidang }}</option>
      </select>
    </div>

    <div class="form-group">
      <label for="pk-tahun">Tahun</label>
      <select id="pk-tahun" v-model="form.tahun">
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>

    <div class="form-group">
      <label for="pk-pj">Penanggung Jawab</label>
      <input id="pk-pj" v-model="form.penanggung_jawab" type="text" />
    </div>

    <div class="form-group">
      <label for="pk-deskripsi">Deskripsi</label>
      <textarea id="pk-deskripsi" v-model="form.deskripsi" rows="3"></textarea>
    </div>

    <div class="form-group">
      <label for="pk-target">Target Capaian</label>
      <textarea id="pk-target" v-model="form.target_capaian" rows="2"></textarea>
    </div>

    <div class="form-group">
      <label for="pk-status">Status</label>
      <select id="pk-status" v-model="form.status">
        <option v-for="s in statusList" :key="s" :value="s">{{ s }}</option>
      </select>
    </div>

    <div class="modal-actions">
      <button type="button" class="btn-small" @click="emit('cancel')">Batal</button>
      <button type="submit" class="btn-submit modal-submit" :disabled="saving">
        {{ saving ? 'Menyimpan...' : 'Simpan' }}
      </button>
    </div>
  </form>
</template>
