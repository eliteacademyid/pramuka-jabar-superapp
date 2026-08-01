<script setup>
import { computed } from 'vue'
import {
  HomeIcon,
  ChartBarIcon,
  PresentationChartLineIcon,
  ArrowsRightLeftIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  collapsed: { type: Boolean, default: false },
  userName: { type: String, default: 'Administrator' },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle', 'logout'])

const navigation = [
  { name: 'Dashboard', path: '/dashboard', icon: HomeIcon },
  { name: 'Statistik', path: '/dashboard/statistik', icon: ChartBarIcon },
  { name: 'Grafik', path: '/dashboard/grafik', icon: PresentationChartLineIcon },
  { name: 'Perbandingan', path: '/dashboard/perbandingan', icon: ArrowsRightLeftIcon }
]

const adminNavigation = [
  { name: 'Kelola User', path: '/admin/users', icon: HomeIcon }
]

const sidebarClass = computed(() => props.collapsed ? 'w-20' : 'w-72')
</script>

<template>
  <aside :class="['flex h-full flex-col border-r border-slate-200 bg-white transition-all duration-300', sidebarClass]">
    <div class="flex items-center justify-between border-b border-slate-200 px-4 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-pramuka-600 text-lg font-bold text-white">P</div>
        <div v-if="!collapsed" class="min-w-0">
          <p class="truncate text-sm font-semibold text-slate-800">Pramuka Jabar</p>
          <p class="truncate text-xs text-slate-500">SuperApp</p>
        </div>
      </div>
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
        <span v-if="!collapsed">{{ item.name }}</span>
      </router-link>

      <router-link
        v-if="isAdmin"
        v-for="item in adminNavigation"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 transition hover:bg-pramuka-50 hover:text-pramuka-700"
        active-class="bg-pramuka-50 text-pramuka-700"
      >
        <component :is="item.icon" class="h-5 w-5" />
        <span v-if="!collapsed">{{ item.name }}</span>
      </router-link>
    </nav>

    <div class="border-t border-slate-200 p-4">
      <div v-if="!collapsed" class="mb-3 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600">
        {{ userName }}
      </div>
      <button class="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-600 transition hover:bg-red-50 hover:text-red-600" @click="emit('logout')">
        <ArrowLeftOnRectangleIcon class="h-5 w-5" />
        <span v-if="!collapsed">Keluar</span>
      </button>
    </div>
  </aside>
</template>
