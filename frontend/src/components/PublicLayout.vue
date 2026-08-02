<template>
  <div class="public-layout">    <header class="topbar">
      <router-link to="/" class="topbar-brand">
        <span class="topbar-logo">⚜️</span>
        <span class="topbar-brand-text">SuperApps-JavaScout <small>Pramuka Jabar</small></span>
      </router-link>
      <nav class="topbar-nav">
        <router-link to="/catalog" class="topbar-link">Marketplace</router-link>
        <ThemeMenu />
        <NotificationBell />
        <router-link to="/login" class="topbar-btn-ghost">Masuk</router-link>
        <router-link to="/register" class="topbar-btn-solid">Daftar</router-link>
      </nav>
    </header>

    <main class="public-main">
      <router-view />
    </main>

    <footer class="public-footer">
      <div class="public-footer-inner">
        <span class="public-footer-brand">⚜️ SuperApps-JavaScout — Pramuka Jawa Barat</span>
        <span class="public-footer-links">
          <router-link to="/catalog">Katalog</router-link>
          <router-link to="/login">Masuk</router-link>
          <router-link to="/register">Daftar</router-link>
        </span>
        <span class="public-footer-copy">&copy; {{ new Date().getFullYear() }} Kwartir Daerah Jawa Barat</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import NotificationBell from './NotificationBell.vue'
import ThemeMenu from './ThemeMenu.vue'
</script>
