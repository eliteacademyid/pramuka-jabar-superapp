<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router = useRouter()
const produk = ref([])
const toko = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const statusLabel = { aktif: 'Aktif', nonaktif: 'Nonaktif' }

onMounted(async () => {
  try {
    try {
      const resToko = await api.get('/penjual/toko')
      toko.value = resToko.data
    } catch (err) {
      if (err.response?.status === 404) {
        router.push('/penjual/toko')
        return
      }
      throw err
    }
    const res = await api.get('/penjual/produk')
    produk.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal memuat produk.'
  } finally {
    loading.value = false
  }
})

async function toggleStatus(p) {
  if (!confirm(`Nonaktifkan produk "${p.nama_produk}"?`)) return
  try {
    await api.put(`/penjual/produk/${p.id}`, {
      nama_produk: p.nama_produk,
      kategori_id: p.kategori_id,
      harga: p.harga,
      stok: p.stok,
      status: p.status === 'aktif' ? 'nonaktif' : 'aktif'
    })
    p.status = p.status === 'aktif' ? 'nonaktif' : 'aktif'
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal mengubah status produk.'
  }
}

async function hapus(p) {
  if (!confirm(`Hapus produk "${p.nama_produk}"?`)) return
  try {
    await api.delete(`/penjual/produk/${p.id}`)
    produk.value = produk.value.filter((x) => x.id !== p.id)
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Gagal menghapus produk.'
  }
}
</script>

<template>
  <div class="penjual-page">
    <div class="page-header">
      <h1>Produk Saya</h1>
      <router-link to="/penjual/produk/baru" class="btn-primary">+ Tambah Produk</router-link>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="loading" class="greeting">Memuat produk...</div>

    <div v-else-if="!toko" class="alert-error">Anda belum memiliki toko.</div>

    <div v-else-if="toko.status !== 'aktif'" class="alert-info">
      Toko Anda belum aktif. Produk baru dapat ditambahkan, tetapi belum tampil di marketplace publik.
    </div>

    <table v-if="produk.length" class="data-table">
      <thead>
        <tr>
          <th>Foto</th>
          <th>Nama Produk</th>
          <th>Kategori</th>
          <th>Harga</th>
          <th>Stok</th>
          <th>Status</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in produk" :key="p.id">
          <td>
            <img v-if="p.foto_url" :src="p.foto_url" class="table-thumb" alt="" />
            <div v-else class="product-photo-placeholder small">Foto</div>
          </td>
          <td>{{ p.nama_produk }}</td>
          <td>{{ p.nama_kategori }}</td>
          <td>Rp {{ p.harga.toLocaleString('id-ID') }}</td>
          <td>{{ p.stok }}</td>
          <td>
            <span :class="['badge-pending', p.status === 'aktif' ? 'toko-aktif' : 'toko-nonaktif']">
              {{ statusLabel[p.status] }}
            </span>
          </td>
          <td>
            <div class="row-actions">
              <router-link :to="`/penjual/produk/${p.id}/edit`" class="btn-small">Edit</router-link>
              <button class="btn-small" @click="toggleStatus(p)">
                {{ p.status === 'aktif' ? 'Nonaktifkan' : 'Aktifkan' }}
              </button>
              <button class="btn-small btn-danger" @click="hapus(p)">Hapus</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-row">Belum ada produk. Klik "+ Tambah Produk" untuk memulai.</div>
  </div>
</template>
