<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Sidebar from '../components/Sidebar.vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const router = useRouter()
const authStore = useAuthStore()

const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)

const userName = computed(() => authStore.user?.nama_lengkap || 'Administrator')
const isAdmin = computed(() => authStore.user?.role === 'admin')

function toggleSidebar() {
  // On mobile: toggle overlay; on desktop: toggle collapsed
  if (window.innerWidth < 1024) {
    sidebarOpen.value = !sidebarOpen.value
  } else {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
}

function closeMobileSidebar() {
  sidebarOpen.value = false
}

function logout() {
  authStore.logout()
  router.replace('/login')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Mobile sidebar overlay -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-20 bg-slate-900/50 lg:hidden"
        @click="closeMobileSidebar"
      />
    </Transition>

    <div class="flex min-h-screen">
      <!-- Desktop sidebar -->
      <div class="hidden lg:block">
        <div class="sticky top-0 h-screen">
          <Sidebar
            :collapsed="sidebarCollapsed"
            :user-name="userName"
            :is-admin="isAdmin"
            @logout="logout"
          />
        </div>
      </div>

      <!-- Mobile sidebar drawer -->
      <Transition name="slide">
        <div v-if="sidebarOpen" class="fixed inset-y-0 left-0 z-30 lg:hidden">
          <Sidebar
            :collapsed="false"
            :user-name="userName"
            :is-admin="isAdmin"
            @logout="logout"
          />
        </div>
      </Transition>

      <!-- Main content -->
      <div class="flex min-w-0 flex-1 flex-col">
        <Navbar :user-name="userName" @toggle-sidebar="toggleSidebar" />
        <main class="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <router-view />
        </main>
        <Footer />
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-enter-active, .slide-leave-active { transition: transform 0.25s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
</style>
