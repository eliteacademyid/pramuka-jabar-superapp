<template>
  <div class="chat-panel">
    <div class="chat-messages">
      <div v-if="!messages.length" class="empty-row">Belum ada pesan</div>
      <div
        v-for="m in messages"
        :key="m.id"
        class="chat-msg"
        :class="{ mine: m.sender_id === me?.user?.id }"
      >
        <div class="chat-msg-head">
          <strong>{{ m.sender_name }}</strong>
          <span>{{ formatTime(m.created_at) }}</span>
        </div>
        <div class="chat-msg-body">{{ m.body }}</div>
      </div>
    </div>
    <div class="chat-input">
      <input v-model="body" maxlength="1000" placeholder="Tulis pesan…" @keyup.enter="send" />
      <button class="btn-small" :disabled="!body.trim()" @click="send">Kirim</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../services/api'
import { getErrorMessage } from '../services/api'
import { meFromCache } from '../services/session'

const props = defineProps({
  conversationId: { type: Number, required: true }
})

const me = ref(meFromCache())
const messages = ref([])
const body = ref('')

async function load() {
  const { data } = await api.get(`/conversations/${props.conversationId}/messages`)
  messages.value = data
}

function formatTime(v) {
  return new Date(v).toLocaleString('id-ID')
}

async function send() {
  try {
    await api.post(`/conversations/${props.conversationId}/messages`, { body: body.value })
    body.value = ''
    await load()
  } catch (err) {
    alert(getErrorMessage(err))
  }
}

onMounted(load)
watch(() => props.conversationId, load)
</script>
