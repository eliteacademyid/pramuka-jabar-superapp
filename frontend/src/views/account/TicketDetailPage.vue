<template>
  <div v-if="ticket" class="page-container">
    <div class="page-header">
      <h2>{{ ticket.ticket_code }}</h2>
      <TicketStatusChip :status="ticket.status" />
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div class="ticket-meta">
      Pesanan <strong>{{ ticket.order_code }}</strong> · {{ ticket.issue_type }} ·
      Dibuka oleh {{ ticket.opened_by }} · Toko {{ ticket.store_name }}
    </div>

    <div class="ticket-desc">
      <h3>Kronologi Awal</h3>
      <p>{{ ticket.description }}</p>
    </div>

    <div v-if="!ticket.messages.length" class="empty-row">Belum ada balasan.</div>
    <div v-else class="ticket-msgs">
      <div
        v-for="m in ticket.messages"
        :key="m.id"
        class="ticket-msg"
        :class="{ mine: m.sender_id === me?.user?.id }"
      >
        <div class="ticket-msg-head">
          <strong>{{ m.sender_name }}</strong>
          <span>{{ new Date(m.created_at).toLocaleString('id-ID') }}</span>
        </div>
        <div class="ticket-msg-body">{{ m.body }}</div>
      </div>
    </div>

    <div v-if="ticket.status !== 'closed'" class="ticket-input">
      <input
        v-model="body"
        maxlength="1000"
        placeholder="Tulis balasan…"
        @keyup.enter="send"
      />
      <button class="btn-small" :disabled="!body.trim()" @click="send">Kirim</button>
    </div>
    <div v-else class="hint">Tiket sudah ditutup — tidak dapat menambah balasan.</div>

    <div class="ticket-status-box">
      <h3>Perbarui Status</h3>
      <div class="ticket-status-actions">
        <button v-if="isAdmin && ticket.status === 'open'" class="btn-small" @click="setStatus('in_review')">
          <i class="fas fa-search"></i> Tinjau (In Review)
        </button>
        <button v-if="isAdmin" class="btn-small" @click="setStatus('resolved')">
          <i class="fas fa-check"></i> Selesaikan (Resolved)
        </button>
        <button v-if="isAdmin || isOpener" class="btn-small" @click="setStatus('closed')">
          <i class="fas fa-lock"></i> Tutup Tiket
        </button>
      </div>
      <div class="field" style="margin-top: 0.6rem">
        <input v-model="statusNote" placeholder="Catatan status (opsional)" />
      </div>
    </div>

    <div class="ticket-history">
      <h3>Riwayat Status</h3>
      <ul class="history-list">
        <li v-for="h in ticket.history" :key="h.id">
          <TicketStatusChip :status="h.status" />
          <span v-if="h.note">({{ h.note }})</span>
          <span class="hint">— {{ h.actor }} · {{ new Date(h.created_at).toLocaleString('id-ID') }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api, { getErrorMessage } from '../../services/api'
import { meFromCache } from '../../services/session'
import TicketStatusChip from '../../components/TicketStatusChip.vue'

const route = useRoute()
const ticket = ref(null)
const body = ref('')
const statusNote = ref('')
const error = ref('')
const me = ref(meFromCache())

const isAdmin = computed(() => me.value && me.value.user.role === 'admin')
const isOpener = computed(() => me.value && ticket.value && ticket.value.opened_by === me.value.user.username)

async function load() {
  const { data } = await api.get(`/tickets/${route.params.id}`)
  ticket.value = data
}

async function send() {
  try {
    await api.post(`/tickets/${ticket.value.id}/messages`, { body: body.value })
    body.value = ''
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

async function setStatus(status) {
  try {
    await api.post(`/tickets/${ticket.value.id}/status`, {
      status,
      note: statusNote.value || null
    })
    statusNote.value = ''
    await load()
  } catch (err) {
    error.value = getErrorMessage(err)
  }
}

onMounted(load)
</script>
