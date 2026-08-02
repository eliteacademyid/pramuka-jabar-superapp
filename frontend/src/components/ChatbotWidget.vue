<script setup>
import { ref, nextTick, onMounted } from 'vue'
import lmsService from '../services/lms'

const isOpen = ref(false)
const inputMessage = ref('')
const isLoading = ref(false)
const chatContainer = ref(null)

const messages = ref([
  {
    role: 'ai',
    text: 'Salam Pramuka! Saya "PRAMUKA AI", asisten pintar kakak. Ada yang bisa saya bantu terkait pelatihan hari ini?'
  }
])

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    scrollToBottom()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userText = inputMessage.value.trim()
  messages.value.push({ role: 'user', text: userText })
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const res = await lmsService.sendChatMessage(userText)
    messages.value.push({ role: 'ai', text: res.data.reply })
  } catch (err) {
    console.error(err)
    let errorMsg = 'Maaf, terjadi kesalahan.'
    if (err.response?.data?.detail) {
      errorMsg = err.response.data.detail
    }
    messages.value.push({ role: 'ai', text: errorMsg })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <div class="chatbot-wrapper">
    <!-- Chat Window -->
    <Transition name="slide-up">
      <div v-if="isOpen" class="chat-window">
        <div class="chat-header">
          <div class="header-info">
            <div class="avatar-ai">🤖</div>
            <div>
              <h4 style="margin: 0; color: white;">Tanya AI</h4>
              <span style="font-size: 0.75rem; opacity: 0.8;">Asisten Pramuka Jabar</span>
            </div>
          </div>
          <button @click="toggleChat" class="close-btn">&times;</button>
        </div>

        <div class="chat-body" ref="chatContainer">
          <div v-for="(msg, idx) in messages" :key="idx"
            :class="['chat-bubble', msg.role === 'ai' ? 'ai-msg' : 'user-msg']">
            {{ msg.text }}
          </div>
          <div v-if="isLoading" class="chat-bubble ai-msg loading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>

        <div class="chat-footer">
          <form @submit.prevent="sendMessage">
            <input type="text" v-model="inputMessage" placeholder="Tanya sesuatu..." :disabled="isLoading" />
            <button type="submit" :disabled="isLoading || !inputMessage.trim()">
              Kirim
            </button>
          </form>
        </div>
      </div>
    </Transition>

    <!-- FAB Button -->
    <button class="fab-btn" @click="toggleChat" :class="{ 'is-active': isOpen }">
      <span v-if="!isOpen">✨ Tanya AI</span>
      <span v-else>&times; Tutup</span>
    </button>
  </div>
</template>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.fab-btn {
  background: var(--maroon);
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.fab-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.fab-btn.is-active {
  background: #333;
}

.chat-window {
  width: 350px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #eee;
}

.chat-header {
  background: var(--maroon);
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar-ai {
  font-size: 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  opacity: 0.8;
}

.close-btn:hover {
  opacity: 1;
}

.chat-body {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-bubble {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
  white-space: pre-wrap;
}

.ai-msg {
  background: white;
  border: 1px solid #eee;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.user-msg {
  background: var(--maroon);
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.chat-footer {
  padding: 1rem;
  background: white;
  border-top: 1px solid #eee;
}

.chat-footer form {
  display: flex;
  gap: 0.5rem;
}

.chat-footer input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}

.chat-footer input:focus {
  border-color: var(--maroon);
}

.chat-footer button {
  background: var(--maroon);
  color: white;
  border: none;
  padding: 0 1rem;
  border-radius: 20px;
  font-weight: 600;
  cursor: pointer;
}

.chat-footer button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Loading Dots */
.loading {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 1rem;
}

.dot {
  width: 6px;
  height: 6px;
  background: #999;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {

  0%,
  80%,
  100% {
    transform: scale(0);
  }

  40% {
    transform: scale(1);
  }
}

/* Transitions */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform-origin: bottom right;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: scale(0.5) translateY(20px);
}
</style>
