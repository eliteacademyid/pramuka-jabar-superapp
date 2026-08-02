<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import api from '../services/api'

const open = ref(false)
const messages = ref([])
const input = ref('')
const busy = ref(false)
const error = ref('')
const box = ref(null)

const SUGGESTIONS = [
  'Cara top up wallet?',
  'Bagaimana cara buka toko?',
  'Bagaimana escrow bekerja?',
  'Cara mengajukan perselisihan?'
]

function toggle() {
  open.value = !open.value
  if (open.value) {
    error.value = ''
    scrollDown()
  }
}

async function send(text) {
  const msg = (text ?? input.value).trim()
  if (!msg || busy.value) return
  input.value = ''
  error.value = ''
  messages.value.push({ role: 'user', text: msg })
  busy.value = true
  scrollDown()
  try {
    const { data } = await api.post('/ai/chat', { message: msg })
    messages.value.push({ role: 'assistant', text: data.reply })
  } catch (e) {
    const detail = e.response?.data?.detail
    error.value = typeof detail === 'string' ? detail : 'Gagal terhubung ke Bantuan AI. Coba lagi.'
  } finally {
    busy.value = false
    scrollDown()
  }
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

function scrollDown() {
  nextTick(() => {
    if (box.value) box.value.scrollTop = box.value.scrollHeight
  })
}

function onDocKey(e) {
  if (e.key === 'Escape' && open.value) open.value = false
}

onMounted(() => document.addEventListener('keydown', onDocKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onDocKey))
</script>

<template>
  <button class="ai-help-btn" type="button" @click="toggle">
    <i class="fas fa-robot"></i> Bantuan AI
  </button>

  <div v-if="open" class="ai-widget">
    <div class="ai-widget-header">
      <span class="ai-widget-title"><i class="fas fa-robot"></i> Bantuan AI</span>
      <button class="ai-widget-close" type="button" @click="open = false">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div ref="box" class="ai-widget-body">
      <div v-if="!messages.length" class="ai-widget-intro">
        <p>Halo! Saya asisten JavaScout. Tanyakan apa saja seputar aplikasi, misalnya:</p>
        <button
          v-for="s in SUGGESTIONS"
          :key="s"
          type="button"
          class="ai-widget-chip"
          @click="send(s)"
        >
          {{ s }}
        </button>
      </div>

      <div
        v-for="(m, i) in messages"
        :key="i"
        class="ai-msg"
        :class="m.role === 'user' ? 'ai-msg--user' : 'ai-msg--bot'"
      >
        {{ m.text }}
      </div>

      <div v-if="busy" class="ai-msg ai-msg--bot ai-msg--typing">
        <span class="ai-dot"></span><span class="ai-dot"></span><span class="ai-dot"></span>
      </div>

      <p v-if="error" class="ai-widget-error">{{ error }}</p>
    </div>

    <div class="ai-widget-footer">
      <input
        v-model="input"
        type="text"
        placeholder="Tulis pertanyaan…"
        maxlength="2000"
        @keydown="onKeydown"
      />
      <button class="ai-widget-send" type="button" :disabled="busy" @click="send()">
        <i class="fas fa-paper-plane"></i>
      </button>
    </div>
  </div>
</template>
