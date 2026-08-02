<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

function goKontak() {
  if (route.name === 'landing') {
    document.getElementById('kontak')?.scrollIntoView({ behavior: 'smooth' })
  } else {
    router.push({ name: 'landing' }).then(() => {
      setTimeout(() => {
        document.getElementById('kontak')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    })
  }
}
</script>

<template>
  <div class="public-layout">
    <header class="topbar">
      <span class="brand">Super Apps Pramuka Jawa Barat</span>
      <nav class="topbar-nav">
        <router-link to="/" class="topbar-link">Beranda</router-link>
        <router-link to="/hub-kegiatan" class="topbar-link">Berita</router-link>
        <router-link to="/data-kepramukaan" class="topbar-link">Data Kepramukaan</router-link>
        <router-link to="/marketplace" class="topbar-link">Marketplace</router-link>
        <a href="#" class="topbar-link" @click.prevent="goKontak">Kontak</a>
        <router-link to="/login" class="topbar-link topbar-link-cta">Masuk</router-link>
      </nav>
    </header>

    <main class="public-main">
      <router-view />
    </main>

    <footer id="kontak" class="public-footer footer-rich">
      <div class="footer-grid">
        <div>
          <h4>Kwartir Daerah Jawa Barat</h4>
          <p>Gerakan Pramuka Jawa Barat</p>
        </div>
        <div>
          <h4>Alamat Sekretariat</h4>
          <p>
            Jl. Gatot Subroto No. 99, Kota Bandung,<br />
            Jawa Barat 40273
          </p>
        </div>
        <div>
          <h4>Kontak</h4>
          <p>Telp/WA: (022) 7000-1234</p>
          <p>Email: info@pramukajabar.or.id</p>
        </div>
        <div>
          <h4>Tautan Cepat</h4>
          <p>
            <router-link to="/hub-kegiatan">Berita</router-link> ·
            <router-link to="/data-kepramukaan">Data Kepramukaan</router-link> ·
            <router-link to="/marketplace">Marketplace</router-link>
          </p>
        </div>
      </div>
      <p class="footer-copy">
        &copy; {{ new Date().getFullYear() }} Kwartir Daerah Jawa Barat
      </p>
    </footer>
  </div>
</template>
