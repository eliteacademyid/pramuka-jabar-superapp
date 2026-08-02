<template>
  <div v-if="hasToken" class="notif-bell-wrap">
    <button class="notif-bell" :class="{ open }" aria-label="Notifikasi" @click="toggle">
      <i class="fas fa-bell"></i>
      <span v-if="count" class="notif-badge">{{ count > 99 ? '99+' : count }}</span>
    </button>

    <div v-if="open" class="notif-backdrop" @click="close"></div>
    <div v-if="open" class="notif-dropdown">
      <header class="notif-dropdown-head">
        <strong>Notifikasi</strong>
        <button v-if="items.some((n) => !n.is_read)" class="notif-read-all" @click="readAll">
          Tandai semua dibaca
        </button>
      </header>
      <div v-if="!items.length" class="empty-row">Belum ada notifikasi</div>
      <ul v-else class="notif-list">
        <li
          v-for="n in items"
          :key="n.id"
          class="notif-item"
          :class="{ unread: !n.is_read }"
          @click="openItem(n)"
        >
          <span class="notif-icon"><i :class="iconFor(n.ntype)"></i></span>
          <span class="notif-body">
            <span class="notif-title">{{ n.title }}</span>
            <span class="notif-text">{{ n.body }}</span>
            <span class="notif-time">{{ timeAgo(n.created_at) }}</span>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()
const hasToken = !!localStorage.getItem('token')
const open = ref(false)
const count = ref(0)
const items = ref([])
let timer = null

function iconFor(t) {
  if (t === 'chat') return 'fas fa-comments'
  if (t === 'wallet') return 'fas fa-wallet'
  return 'fas fa-box-open'
}

function timeAgo(v) {
  const diff = (Date.now() - new Date(v).getTime()) / 1000
  if (diff < 60) return 'baru saja'
  if (diff < 3600) return `${Math.floor(diff / 60)} mnt lalu`
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`
  return new Date(v).toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}

async function loadCount() {
  try {
    const { data } = await api.get('/notifications/unread-count')
    count.value = data.count
  } catch {
    /* ignore */
  }
}

async function toggle() {
  open.value = !open.value
  if (open.value) {
    try {
      const { data } = await api.get('/notifications')
      items.value = data
      readAll()
    } catch {
      /* ignore */
    }
  }
}

function close() {
  open.value = false
}

async function readAll() {
  try {
    await api.post('/notifications/read-all')
    items.value = items.value.map((n) => ({ ...n, is_read: true }))
    count.value = 0
  } catch {
    /* ignore */
  }
}

function openItem(n) {
  router.push(n.link || '/')
  close()
}

onMounted(() => {
  if (hasToken) {
    loadCount()
    timer = setInterval(loadCount, 10000)
  }
})

onBeforeUnmount(() => clearInterval(timer))
</script>
