<script setup>
import { Bars3Icon } from '@heroicons/vue/24/outline'

const props = defineProps({
  userName: { type: String, default: 'Administrator' }
})

const emit = defineEmits(['toggle-sidebar'])
</script>

<template>
  <header class="border-b border-slate-200 bg-white/90 backdrop-blur">
    <div class="flex items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
      <div class="flex items-center gap-3">
        <button class="rounded-xl border border-slate-200 p-2 text-slate-600 hover:bg-slate-100" @click="emit('toggle-sidebar')">
          <Bars3Icon class="h-5 w-5" />
        </button>
        <div>
          <p class="text-sm font-semibold text-slate-800">Dashboard Operasional</p>
          <p class="text-sm text-slate-500">Pramuka Kwarda Jabar SuperApp</p>
        </div>
      </div>
      <div class="rounded-full bg-pramuka-50 px-3 py-1 text-sm font-medium text-pramuka-700">
        {{ userName }}
      </div>
    </div>
  </header>
</template>
