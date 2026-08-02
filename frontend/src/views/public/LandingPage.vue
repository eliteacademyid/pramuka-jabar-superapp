<template>
  <div class="landing">
    <section class="landing-hero">
      <div class="landing-hero-inner">
        <div class="landing-logo"><span>⚜️</span></div>
        <span class="landing-eyebrow">Pramuka Jawa Barat</span>
        <h1>SuperApps-JavaScout</h1>
        <p>
          Satu aplikasi anggota pramuka untuk pemberdayaan ekonomi — katalog
          marketplace UMKM &amp; toko anggota Pramuka dalam satu tempat.
        </p>
        <form class="landing-search" @submit.prevent="doSearch">
          <i class="fas fa-search"></i>
          <SearchSuggest
            v-model="keyword"
            placeholder="Cari produk, mis. kopi, kerajinan…"
            @submit="doSearch"
          />
          <span class="landing-search-sep"></span>
          <i class="fas fa-location-dot"></i>
          <input
            v-model="city"
            type="text"
            placeholder="Kota, mis. Bandung"
            aria-label="Cari lokasi"
          />
          <button type="submit" class="btn-landing-search">
            <i class="fas fa-magnifying-glass"></i> Cari
          </button>
        </form>
        <div class="landing-actions">
          <router-link to="/catalog" class="btn-landing-solid">
            <i class="fas fa-store"></i> Jelajahi Katalog
          </router-link>
          <router-link to="/register" class="btn-landing-ghost">
            <i class="fas fa-user-plus"></i> Daftar Gratis
          </router-link>
        </div>
        <span class="landing-note">Sudah punya akun? <router-link to="/login">Masuk</router-link></span>
      </div>
    </section>

    <section class="landing-stats">
      <div class="landing-stat">
        <span class="landing-stat-num">100+</span>
        <span class="landing-stat-label">Produk UMKM</span>
      </div>
      <div class="landing-stat">
        <span class="landing-stat-num">50+</span>
        <span class="landing-stat-label">Toko Aktif</span>
      </div>
      <div class="landing-stat">
        <span class="landing-stat-num">100%</span>
        <span class="landing-stat-label">Aman Escrow</span>
      </div>
      <div class="landing-stat">
        <span class="landing-stat-num">24/7</span>
        <span class="landing-stat-label">Layanan</span>
      </div>
    </section>

    <section class="landing-section">
      <h2 class="landing-title">Kenapa SuperApps-JavaScout?</h2>
      <p class="landing-subtitle">Ekonomi Pramuka yang berdaya saing</p>
      <div class="landing-features">
        <router-link :to="{ name: 'catalog' }" class="landing-feature">
          <i class="fas fa-store"></i>
          <h3>Marketplace</h3>
          <p>Jelajahi produk unggulan UMKM dan toko anggota Pramuka Jawa Barat.</p>
        </router-link>
        <router-link :to="{ name: 'wallet' }" class="landing-feature">
          <i class="fas fa-wallet"></i>
          <h3>Wallet &amp; Escrow</h3>
          <p>Pembayaran aman lewat escrow — dana baru dilepas saat pesanan diterima.</p>
        </router-link>
        <router-link :to="{ name: 'register' }" class="landing-feature">
          <i class="fas fa-shop"></i>
          <h3>Buka Toko Sendiri</h3>
          <p>Anggota &amp; UMKM bisa membuka toko dan berjualan dengan mudah.</p>
        </router-link>
        <router-link :to="{ name: 'chat' }" class="landing-feature">
          <i class="fas fa-comments"></i>
          <h3>Chat Penjual</h3>
          <p>Komunikasi langsung pembeli–penjual untuk transaksi yang lancar.</p>
        </router-link>
      </div>
    </section>

    <section class="landing-section landing-section-alt">
      <h2 class="landing-title">Kategori Populer</h2>
      <p class="landing-subtitle">Mulai belanja dari kategori favoritmu</p>
      <div class="landing-categories">
        <router-link
          v-for="c in cats"
          :key="c.slug"
          :to="{ name: 'catalog', query: { category: c.slug } }"
          class="landing-category"
        >
          <i :class="c.icon"></i>
          <span>{{ c.name }}</span>
        </router-link>
      </div>
    </section>

    <section class="landing-cta">
      <h2>Siap berjualan di marketplace Pramuka?</h2>
      <p>Buka tokomu hari ini — aplikasi dari Kwartir Daerah Jawa Barat yang terbuka untuk seluruh Indonesia.</p>
      <router-link to="/register" class="btn-landing-cta">
        <i class="fas fa-user-plus"></i> Daftar &amp; Buka Toko
      </router-link>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SearchSuggest from '../../components/SearchSuggest.vue'

const router = useRouter()
const keyword = ref('')
const city = ref('')

function doSearch() {
  const q = keyword.value.trim()
  const c = city.value.trim()
  const query = {}
  if (q) query.q = q
  if (c) query.city = c
  router.push({ name: 'catalog', query })
}

const cats = [
  { slug: 'makanan', name: 'Makanan', icon: 'fas fa-utensils' },
  { slug: 'minuman', name: 'Minuman', icon: 'fas fa-mug-hot' },
  { slug: 'kerajinan', name: 'Kerajinan', icon: 'fas fa-hand-sparkles' },
  { slug: 'fashion', name: 'Fashion', icon: 'fas fa-tshirt' },
  { slug: 'jasa', name: 'Jasa', icon: 'fas fa-handshake' },
  { slug: 'perlengkapan', name: 'Perlengkapan Pramuka', icon: 'fas fa-campground' },
  { slug: 'camping', name: 'Peralatan Berkemah', icon: 'fas fa-tent' },
  { slug: 'lainnya', name: 'Lainnya', icon: 'fas fa-box' }
]
</script>
