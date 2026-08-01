<template>
  <div class="page-container">
    <div class="page-header"><h2>{{ isEdit ? 'Edit Produk' : 'Produk Baru' }}</h2></div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div class="form-group" style="max-width: 480px">
      <label>Nama</label>
      <input v-model="form.name" required />
      <label>Kategori</label>
      <select v-model="form.category_id">
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <label>Harga (Rp)</label>
      <input v-model.number="form.price" type="number" min="1" required />
      <label>Stok</label>
      <input v-model.number="form.stock" type="number" min="0" required />
      <label>Unit (pcs/bungkus/cup…)</label>
      <input v-model="form.unit" />
      <label>URL Gambar (opsional, sintetis)</label>
      <input v-model="imageUrl" @change="pushImage" />
      <div class="hint">Gambar saat ini: {{ form.images?.join(', ') || '—' }}</div>
      <label>Status</label>
      <select v-model="form.status">
        <option value="draft">Draft</option>
        <option value="active">Aktif (tampil publik)</option>
        <option value="archived">Arsip</option>
      </select>
      <label>Deskripsi</label>
      <textarea v-model="form.description" rows="4"></textarea>

      <button class="btn-submit" style="max-width: 220px" @click="save">Simpan</button>
      <router-link class="back-link" :to="{ name: 'seller-products' }">← Kembali</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getErrorMessage } from '../../services/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const categories = ref([])
const error = ref('')
const imageUrl = ref('')
const form = ref({
  name: '',
  category_id: null,
  price: null,
  stock: 0,
  unit: '',
  images: [],
  status: 'draft',
  description: ''
})

function pushImage() {
  if (imageUrl.value.trim()) form.value.images.push(imageUrl.value.trim())
  imageUrl.value = ''
}

async function save() {
  try {
    if (isEdit.value) {
      await api.put(`/seller/products/${route.params.id}`, form.value)
    } else {
      await api.post('/seller/products', form.value)
    }
    router.push({ name: 'seller-products' })
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

onMounted(async () => {
  const { data } = await api.get('/categories')
  categories.value = data
  if (isEdit.value) {
    const { data: p } = await api.get(`/seller/products/${route.params.id}`)
    form.value = {
      name: p.name,
      category_id: p.category_id,
      price: Number(p.price),
      stock: p.stock,
      unit: p.unit || '',
      images: p.images || [],
      status: p.status,
      description: p.description || ''
    }
  }
})
</script>
