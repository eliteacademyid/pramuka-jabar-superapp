<template>
  <div class="public-layout">
    <header class="topbar">
      <span class="brand">Super Apps Pramuka Jawa Barat</span>
    </header>

    <main class="public-main">
      <router-view />
    </main>

    <footer class="public-footer">
      <span>&copy; {{ new Date().getFullYear() }} Kwartir Daerah Jawa Barat</span>
    </footer>
  </div>
</template>
