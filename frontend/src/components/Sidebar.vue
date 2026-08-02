<script setup>
import { computed } from 'vue'
import {
  HomeIcon,
  ChartBarIcon,
  PresentationChartLineIcon,
  ArrowsRightLeftIcon,
  ClipboardDocumentListIcon,
  DocumentChartBarIcon,
  ClipboardDocumentCheckIcon,
  UsersIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  collapsed: { type: Boolean, default: false },
  userName: { type: String, default: 'Administrator' },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle', 'logout'])

const navigation = [
  {
    group: 'Dashboard',
    items: [
      { name: 'Beranda', path: '/dashboard', icon: HomeIcon },
      { name: 'Statistik', path: '/dashboard/statistik', icon: ChartBarIcon },
      { name: 'Grafik', path: '/dashboard/grafik', icon: PresentationChartLineIcon },
      { name: 'Perbandingan', path: '/dashboard/perbandingan', icon: ArrowsRightLeftIcon }
    ]
  },
  {
    group: 'E-Reporting',
    items: [
      { name: 'Realisasi', path: '/e-reporting/realisasi', icon: ClipboardDocumentListIcon },
      { name: 'Laporan', path: '/e-reporting/laporan', icon: DocumentChartBarIcon },
      { name: 'Approval', path: '/e-reporting/approval', icon: ClipboardDocumentCheckIcon }
    ]
  }
]

const adminNavigation = [
  { name: 'Kelola User', path: '/admin/users', icon: UsersIcon }
]

const sidebarClass = computed(() => (props.collapsed ? 'w-20' : 'w-72'))
</script>

<template>
  <aside
    :class="[
      'flex h-full flex-col border-r border-slate-200 bg-white transition-all duration-300',
      sidebarClass
    ]"
  >
    <!-- Logo -->
    <div class="flex items-center justify-between border-b border-slate-200 px-4 py-4">
      <div class="flex items-center gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-pramuka-600 text-lg font-bold text-white"
        >
          P
        </div>
        <div v-if="!collapsed" class="min-w-0">
          <p class="truncate text-sm font-semibold text-slate-800">Pramuka Jabar</p>
          <p class="truncate text-xs text-slate-500">SuperApp</p>
        </div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto px-3 py-4">
      <template v-for="section in navigation" :key="section.group">
        <!-- Group label -->
        <p
          v-if="!collapsed"
          class="mb-1 mt-4 px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400 first:mt-0"
        >
          {{ section.group }}
        </p>
        <div v-else class="my-2 mx-3 border-t border-slate-100" />

        <router-link
          v-for="item in section.items"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-pramuka-50 hover:text-pramuka-700"
          active-class="bg-pramuka-50 text-pramuka-700"
          :title="collapsed ? item.name : undefined"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          <span v-if="!collapsed">{{ item.name }}</span>
        </router-link>
      </template>

      <!-- Admin section -->
      <template v-if="isAdmin">
        <p
          v-if="!collapsed"
          class="mb-1 mt-4 px-3 text-[10px] font-bold uppercase tracking-widest text-slate-400"
        >
          Admin
        </p>
        <div v-else class="my-2 mx-3 border-t border-slate-100" />

        <router-link
          v-for="item in adminNavigation"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-pramuka-50 hover:text-pramuka-700"
          active-class="bg-pramuka-50 text-pramuka-700"
          :title="collapsed ? item.name : undefined"
        >
          <component :is="item.icon" class="h-5 w-5 shrink-0" />
          <span v-if="!collapsed">{{ item.name }}</span>
        </router-link>
      </template>
    </nav>

    <!-- User & logout -->
    <div class="border-t border-slate-200 p-4">
      <div
        v-if="!collapsed"
        class="mb-3 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-600 truncate"
      >
        {{ userName }}
      </div>
      <button
        class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-red-50 hover:text-red-600"
        :title="collapsed ? 'Keluar' : undefined"
        @click="emit('logout')"
      >
        <ArrowLeftOnRectangleIcon class="h-5 w-5 shrink-0" />
        <span v-if="!collapsed">Keluar</span>
      </button>
    </div>
  </aside>
</template>
