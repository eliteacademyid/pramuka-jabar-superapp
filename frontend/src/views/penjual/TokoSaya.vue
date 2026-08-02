<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../../services/api'

const toko = ref(null)
const mode = ref('load') // load | create | edit
const loading = ref(true)
const errorMessage = ref('')
const saving = ref(false)

const form = ref({
  nama_toko: '',
  deskripsi: '',
  nama_pemilik_rekening: '',
  nama_bank: '',
  nomor_rekening: '',
  nomor_wa: ''
})

const statusLabel = {
  pending: 'Menunggu Verifikasi',
  aktif: 'Aktif',
  nonaktif: 'Nonaktif'
}

const canEdit = computed(() => toko.value && toko.value.status !== 'pending')

onMounted(async () => {
  try {
    try {
      const res = await api.get('/penjual/toko')
      toko.value = res.data
    } catch (err) {
      if (err.response?.status === 404) {
        mode.value = 'create'
        toko.value = null
      } else {
        throw err
      }
    }
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat toko.'
  } finally {
    loading.value = false
  }
})

function mulaiEdit() {
  form.value = {
    nama_toko: toko.value.nama_toko,
    deskripsi: toko.value.deskripsi || '',
    nama_pemilik_rekening: toko.value.nama_pemilik_rekening || '',
    nama_bank: toko.value.nama_bank || '',
    nomor_rekening: toko.value.nomor_rekening || '',
    nomor_wa: toko.value.nomor_wa || ''
  }
  mode.value = 'edit'
}

async function submit() {
  errorMessage.value = ''
  if (!form.value.nama_toko.trim()) {
    errorMessage.value = 'Nama toko wajib diisi.'
    return
  }
  if (!form.value.nama_pemilik_rekening.trim() || !form.value.nama_bank.trim() || !form.value.nomor_rekening.trim()) {
    errorMessage.value = 'Data rekening (pemilik, bank, nomor) wajib diisi.'
    return
  }
  saving.value = true
  try {
    const payload = {
      nama_toko: form.value.nama_toko,
      deskripsi: form.value.deskripsi || null,
      nama_pemilik_rekening: form.value.nama_pemilik_rekening,
      nama_bank: form.value.nama_bank,
      nomor_rekening: form.value.nomor_rekening,
      nomor_wa: form.value.nomor_wa || null
    }
    let res
    if (mode.value === 'create') res = await api.post('/penjual/toko', payload)
    else res = await api.put('/penjual/toko', payload)
    toko.value = res.data
    mode.value = 'load'
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menyimpan toko.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="penjual-page">
    <div class="page-header">
      <h1>Toko Saya</h1>
      <p>Kelola profil toko, termasuk rekening tujuan pembayaran.</p>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="loading" class="greeting">Memuat...</div>

    <div v-else-if="mode === 'load' && toko">
      <div class="toko-status-card">
        <strong>{{ toko.nama_toko }}</strong>
        <span :class="['badge-pending', `toko-${toko.status}`]">{{ statusLabel[toko.status] }}</span>
      </div>

      <div v-if="toko.status === 'pending'" class="alert-info">
        Toko Anda sedang menunggu verifikasi admin. Produk hanya tampil di marketplace setelah toko aktif.
      </div>
      <div v-if="toko.status === 'nonaktif'" class="alert-error">
        Toko Anda dinonaktifkan. Hubungi admin untuk informasi lebih lanjut.
      </div>

      <div class="modal-card toko-info">
        <p v-if="toko.deskripsi"><strong>Deskripsi:</strong> {{ toko.deskripsi }}</p>
        <div class="rekening-box">
          <h3>Rekening Tujuan</h3>
          <div class="rekening-row"><span>Bank</span><strong>{{ toko.nama_bank }}</strong></div>
          <div class="rekening-row"><span>Nomor Rekening</span><strong>{{ toko.nomor_rekening }}</strong></div>
          <div class="rekening-row"><span>Atas Nama</span><strong>{{ toko.nama_pemilik_rekening }}</strong></div>
          <div class="rekening-row" v-if="toko.nomor_wa"><span>WhatsApp</span><strong>{{ toko.nomor_wa }}</strong></div>
        </div>
        <button v-if="canEdit" class="btn-primary" @click="mulaiEdit">Edit Toko</button>
      </div>
    </div>

    <form
      v-else
      class="modal-card toko-form"
      @submit.prevent="submit"
    >
      <h2>{{ mode === 'create' ? 'Buka Toko Baru' : 'Edit Toko' }}</h2>
      <div class="form-group">
        <label>Nama Toko</label>
        <input v-model="form.nama_toko" type="text" placeholder="Nama toko" required />
      </div>
      <div class="form-group">
        <label>Deskripsi (opsional)</label>
        <textarea v-model="form.deskripsi" rows="3" placeholder="Deskripsi singkat toko"></textarea>
      </div>
      <h3 class="form-section">Rekening Tujuan Pembayaran</h3>
      <div class="form-group">
        <label>Nama Pemilik Rekening</label>
        <input v-model="form.nama_pemilik_rekening" type="text" required />
      </div>
      <div class="form-group">
        <label>Nama Bank</label>
        <input v-model="form.nama_bank" type="text" placeholder="contoh: BCA" required />
      </div>
      <div class="form-group">
        <label>Nomor Rekening</label>
        <input v-model="form.nomor_rekening" type="text" required />
      </div>
      <div class="form-group">
        <label>Nomor WhatsApp (opsional)</label>
        <input v-model="form.nomor_wa" type="text" placeholder="08xx..." />
      </div>
      <div class="form-actions">
        <button class="btn-submit" type="submit" :disabled="saving">
          {{ saving ? 'Menyimpan...' : 'Simpan' }}
        </button>
        <button
          v-if="mode === 'edit'"
          type="button"
          class="btn-cancel"
          @click="mode = 'load'"
        >Batal</button>
      </div>
    </form>
  </div>
</template>
