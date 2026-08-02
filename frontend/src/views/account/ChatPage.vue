<template>
  <div class="page-container chat-page">
    <div class="page-header">
      <h2>{{ sellerOnly ? 'Pesan Masuk (Penjual)' : 'Chat' }}</h2>
    </div>

    <div class="chat-layout">
      <aside class="chat-list">
        <div v-if="!filtered.length" class="empty-row">
          {{ sellerOnly ? 'Belum ada pesan masuk dari pembeli.' : 'Belum ada percakapan.<br />Mulai chat dari halaman produk.' }}
        </div>
        <button
          v-for="c in filtered"
          :key="c.id"
          class="chat-list-item"
          :class="{ active: c.id === activeId }"
          @click="open(c.id)"
        >
          <span class="chat-avatar">{{ initial(c.store_name) }}</span>
          <span class="chat-list-body">
            <span class="chat-list-name">
              {{ sellerOnly ? (c.participants.find((p) => p !== me?.user?.username) || 'Pembeli') : c.store_name }}
              <span class="chat-list-badge" v-if="c.unread_count">{{ c.unread_count }}</span>
            </span>
            <span class="chat-list-sub">{{ c.product_name || ('Pesanan ' + c.order_code) }}</span>
            <span class="chat-list-preview">{{ c.last_message || 'Belum ada pesan' }}</span>
          </span>
          <span class="chat-list-time">{{ shortTime(c.last_message_at || c.created_at) }}</span>
        </button>
      </aside>

      <section class="chat-thread">
        <template v-if="active">
          <header class="chat-thread-head">
            <span class="chat-avatar">{{ initial(active.store_name) }}</span>
            <span>
              <strong>{{ sellerOnly ? (active.participants.find((p) => p !== me?.user?.username) || 'Pembeli') : active.store_name }}</strong>
              <span class="chat-thread-sub">{{ active.product_name || ('Pesanan ' + active.order_code) }}</span>
            </span>
          </header>
          <ChatPanel :conversation-id="active.id" />
        </template>
        <div v-else class="empty-row chat-thread-empty">Pilih percakapan di samping</div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../services/api'
import { meFromCache } from '../../services/session'
import ChatPanel from '../../components/ChatPanel.vue'

const props = defineProps({
  sellerOnly: { type: Boolean, default: false }
})

const route = useRoute()
const router = useRouter()
const me = ref(meFromCache())
const convs = ref([])
const activeId = ref(null)
let timer = null

const filtered = computed(() =>
  props.sellerOnly ? convs.value.filter((c) => c.i_am_seller) : convs.value
)

const active = computed(() => filtered.value.find((c) => c.id === activeId.value))

function initial(name) {
  return (name || '?').trim().charAt(0).toUpperCase()
}

function shortTime(v) {
  if (!v) return ''
  return new Date(v).toLocaleString('id-ID', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

async function load() {
  const { data } = await api.get('/conversations')
  convs.value = data
  if (!activeId.value && filtered.value.length) {
    open(filtered.value[0].id, { replace: true })
  } else if (route.params.id && !filtered.value.find((c) => c.id === activeId.value)) {
    open(filtered.value[0]?.id, { replace: true })
  }
}

function open(id, opts = {}) {
  activeId.value = id
  router[opts.replace ? 'replace' : 'push']({ name: 'chat-detail', params: { id } })
}

onMounted(() => {
  activeId.value = Number(route.params.id) || null
  load()
  timer = setInterval(load, 5000)
})

onBeforeUnmount(() => clearInterval(timer))
</script>
