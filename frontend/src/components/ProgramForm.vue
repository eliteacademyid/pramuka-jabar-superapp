<template>
  <BaseCard class="max-w-2xl mx-auto">
    <h2 class="text-xl font-bold text-slate-800 mb-6">
      {{ mode === 'edit' ? 'Edit Program' : 'Tambah Program Baru' }}
    </h2>

    <form @submit.prevent="onSubmit" class="space-y-5">
      <!-- Program Name -->
      <BaseInput
        label="Nama Program"
        placeholder="Masukkan nama program"
        v-model="form.nama"
        :error="errors.nama"
        required
      />

      <!-- Description -->
      <BaseTextarea
        label="Deskripsi"
        placeholder="Masukkan deskripsi program"
        v-model="form.deskripsi"
        :error="errors.deskripsi"
        rows="4"
      />

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Year -->
        <BaseInput
          label="Tahun"
          type="number"
          placeholder="Contoh: 2026"
          v-model="form.tahun"
          :error="errors.tahun"
          required
        />

        <!-- Status -->
        <BaseSelect
          label="Status"
          placeholder="Pilih Status"
          :options="statusOptions"
          v-model="form.status"
          :error="errors.status"
          required
        />
      </div>

      <!-- Organisasi -->
      <BaseSelect
        label="Organisasi"
        placeholder="Pilih Organisasi"
        :options="organisasiOptions"
        v-model="form.organisasi_id"
        :error="errors.organisasi_id"
        required
      />

      <!-- Action Buttons -->
      <div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
        <BaseButton variant="secondary" type="button" @click="$emit('cancel')">
          Batal
        </BaseButton>
        <BaseButton type="submit" :loading="saving">
          Simpan
        </BaseButton>
      </div>
    </form>
  </BaseCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseTextarea from '@/components/common/BaseTextarea.vue'
import BaseSelect from '@/components/common/BaseSelect.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import api from '@/api/axios'

const props = defineProps({
  mode: { type: String, default: 'create' },
  initialData: { type: Object, default: () => null },
  saving: { type: Boolean, default: false }
})

const emit = defineEmits(['submit', 'cancel'])

const form = ref({
  nama: '',
  deskripsi: '',
  tahun: new Date().getFullYear(),
  status: 'aktif',
  organisasi_id: ''
})

const errors = ref({
  nama: '',
  deskripsi: '',
  tahun: '',
  status: '',
  organisasi_id: ''
})

const statusOptions = [
  { value: 'aktif', label: 'Aktif' },
  { value: 'selesai', label: 'Selesai' },
  { value: 'ditangguhkan', label: 'Ditangguhkan' }
]

const organisasiOptions = ref([])

onMounted(async () => {
  if (props.initialData) {
    form.value = { ...form.value, ...props.initialData }
  }
  await loadOrganisasi()
})

async function loadOrganisasi() {
  try {
    const res = await api.get('/organisasi')
    organisasiOptions.value = res.data.map(org => ({
      value: org.id,
      label: org.nama
    }))
  } catch (err) {
    console.error('Gagal memuat organisasi:', err)
  }
}

function onSubmit() {
  errors.value = {
    nama: '',
    deskripsi: '',
    tahun: '',
    status: '',
    organisasi_id: ''
  }

  let isValid = true

  if (!form.value.nama || !form.value.nama.trim()) {
    errors.value.nama = 'Nama program wajib diisi'
    isValid = false
  } else if (form.value.nama.length > 150) {
    errors.value.nama = 'Nama program tidak boleh lebih dari 150 karakter'
    isValid = false
  }

  const tahunNum = Number(form.value.tahun)
  if (!form.value.tahun) {
    errors.value.tahun = 'Tahun wajib diisi'
    isValid = false
  } else if (isNaN(tahunNum) || tahunNum < 1900 || tahunNum > 2100) {
    errors.value.tahun = 'Tahun harus berupa angka antara 1900 dan 2100'
    isValid = false
  }

  if (!form.value.status) {
    errors.value.status = 'Status wajib dipilih'
    isValid = false
  }

  if (!form.value.organisasi_id) {
    errors.value.organisasi_id = 'Organisasi wajib dipilih'
    isValid = false
  }

  if (isValid) {
    emit('submit', {
      nama: form.value.nama.trim(),
      deskripsi: form.value.deskripsi ? form.value.deskripsi.trim() : null,
      tahun: tahunNum,
      status: form.value.status,
      organisasi_id: Number(form.value.organisasi_id)
    })
  }
}
</script>

<style scoped>
/* No custom styles */
</style>
