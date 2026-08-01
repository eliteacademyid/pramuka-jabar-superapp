<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import Sidebar from '../components/Sidebar.vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'

const router = useRouter()
const authStore = useAuthStore()

const sidebarCollapsed = ref(false)

const userName = computed(() => authStore.user?.nama_lengkap || 'Administrator')

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

function logout() {
  authStore.logout()
  router.replace('/login')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <div class="flex min-h-screen">
      <div class="hidden lg:block">
        <Sidebar :collapsed="sidebarCollapsed" :user-name="userName" @logout="logout" />
      </div>

      <div v-if="sidebarCollapsed" class="fixed inset-y-0 left-0 z-30 lg:hidden">
        <Sidebar :collapsed="true" :user-name="userName" @logout="logout" />
      </div>

      <div class="flex-1">
        <Navbar :user-name="userName" @toggle-sidebar="toggleSidebar" />
        <main class="px-4 py-6 sm:px-6 lg:px-8">
          <router-view />
        </main>
        <Footer />
      </div>
    </div>
  </div>
</template>
