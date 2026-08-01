<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useGlobalStore } from '../store/global'
import {
  HomeIcon,
  ChartBarIcon,
  PresentationChartLineIcon,
  ArrowsRightLeftIcon,
  ArrowLeftOnRectangleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const globalStore = useGlobalStore()

const navigation = [
  { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
  { name: 'Statistik', path: '/dashboard/statistik', icon: ChartBarIcon },
  { name: 'Grafik', path: '/dashboard/grafik', icon: PresentationChartLineIcon },
  { name: 'Perbandingan', path: '/dashboard/perbandingan', icon: ArrowsRightLeftIcon }
]

const sidebarCollapsed = computed(() => globalStore.sidebarCollapsed)

function toggleSidebar() {
  globalStore.setSidebarCollapsed(!globalStore.sidebarCollapsed)
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <div class="flex min-h-screen">
      <aside :class="['fixed inset-y-0 left-0 z-30 flex flex-col border-r border-slate-200 bg-white transition-all duration-300 lg:static', sidebarCollapsed ? 'w-20' : 'w-72']">
        <div class="flex items-center justify-between border-b border-slate-200 px-4 py-4">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-pramuka-600 text-lg font-bold text-white">P</div>
            <div v-if="!sidebarCollapsed" class="min-w-0">
              <p class="truncate text-sm font-semibold text-slate-800">Pramuka Jabar</p>
              <p class="truncate text-xs text-slate-500">SuperApp</p>
            </div>
          </div>
          <button class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden" @click="toggleSidebar">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>

        <nav class="flex-1 space-y-1 px-3 py-4">
          <router-link
            v-for="item in navigation"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 transition hover:bg-pramuka-50 hover:text-pramuka-700"
            active-class="bg-pramuka-50 text-pramuka-700"
          >
            <component :is="item.icon" class="h-5 w-5" />
            <span v-if="!sidebarCollapsed">{{ item.name }}</span>
          </router-link>
        </nav>

        <div class="border-t border-slate-200 p-4">
          <button class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 transition hover:bg-red-50 hover:text-red-600" @click="logout">
            <ArrowLeftOnRectangleIcon class="h-5 w-5" />
            <span v-if="!sidebarCollapsed">Keluar</span>
          </button>
        </div>
      </aside>

      <div class="flex-1 lg:ml-0">
        <header class="border-b border-slate-200 bg-white/90 backdrop-blur">
          <div class="flex items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <div class="flex items-center gap-3">
              <button class="rounded-xl border border-slate-200 p-2 text-slate-600 hover:bg-slate-100" @click="toggleSidebar">
                <Bars3Icon class="h-5 w-5" />
              </button>
              <div>
                <p class="text-sm font-semibold text-slate-800">Dashboard Operasional</p>
                <p class="text-sm text-slate-500">Pramuka Kwarda Jabar SuperApp</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <div class="rounded-full bg-pramuka-50 px-3 py-1 text-sm font-medium text-pramuka-700">
                {{ authStore.user?.nama_lengkap || 'Administrator' }}
              </div>
            </div>
          </div>
        </header>

        <main class="px-4 py-6 sm:px-6 lg:px-8">
          <router-view />
        </main>

        <footer class="border-t border-slate-200 bg-white px-4 py-4 text-center text-sm text-slate-500 sm:px-6 lg:px-8">
          © {{ new Date().getFullYear() }} Kwartir Daerah Jawa Barat • Pramuka SuperApp
        </footer>
      </div>
    </div>
  </div>
</template>
