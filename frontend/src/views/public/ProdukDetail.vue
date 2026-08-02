<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'

const route = useRoute()
const router = useRouter()

const produk = ref(null)
const jumlah = ref(1)
const loading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const res = await api.get(`/public/marketplace/produk/${route.params.id}`)
    produk.value = res.data
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Produk tidak ditemukan.'
  } finally {
    loading.value = false
  }
})

function naik() {
  if (jumlah.value < produk.value.stok) jumlah.value += 1
}
function turun() {
  if (jumlah.value > 1) jumlah.value -= 1
}

function beliSekarang() {
  router.push({
    name: 'marketplace-checkout',
    query: { produk_id: produk.value.id, jumlah: jumlah.value }
  })
}
</script>

<template>
  <div class="marketplace-page">
    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <div v-if="produk" class="produk-detail">
      <div class="produk-detail-photo">
        <img v-if="produk.foto_url" :src="produk.foto_url" alt="foto produk" />
        <div v-else class="product-photo-placeholder">Foto</div>
      </div>

      <div class="produk-detail-info">
        <router-link to="/marketplace" class="back-link">Kembali ke Marketplace</router-link>
        <span class="badge badge-cat">{{ produk.nama_kategori }}</span>
        <h1>{{ produk.nama_produk }}</h1>
        <div class="product-harga besar">Rp {{ produk.harga.toLocaleString('id-ID') }}</div>
        <p class="stok-line">
          Stok tersedia:
          <span :class="produk.stok > 0 ? 'stok-ada' : 'stok-habis'">
            {{ produk.stok > 0 ? produk.stok + ' buah' : 'Habis' }}
          </span>
        </p>
        <p v-if="produk.deskripsi" class="produk-deskripsi">{{ produk.deskripsi }}</p>

        <div class="penjual-info">
          <strong>{{ produk.nama_toko }}</strong>
          <span>Dijual melalui Marketplace Pramuka</span>
        </div>

        <div class="qty-row" v-if="produk.stok > 0">
          <button class="btn-small" @click="turun">-</button>
          <span class="qty-value">{{ jumlah }}</span>
          <button class="btn-small" @click="naik">+</button>
          <span class="qty-hint">(max {{ produk.stok }})</span>
        </div>

        <button
          class="btn-primary btn-beli"
          :disabled="produk.stok <= 0"
          @click="beliSekarang"
        >
          {{ produk.stok > 0 ? 'Beli Sekarang' : 'Produk Habis' }}
        </button>
      </div>
    </div>

    <div v-else-if="loading" class="greeting">Memuat produk...</div>
  </div>
</template>
