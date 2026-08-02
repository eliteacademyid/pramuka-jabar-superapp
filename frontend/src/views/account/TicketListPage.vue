<template>
  <div class="page-container">
    <div class="page-header">
      <h2>Perselisihan (Tiket)</h2>
      <router-link :to="{ name: 'ticket-new' }" class="btn-submit" style="text-decoration: none">
        <i class="fas fa-plus"></i> Ajukan Perselisihan
      </router-link>
    </div>

    <div v-if="error" class="alert-error">{{ error }}</div>

    <div v-if="!tickets.length" class="empty-row">Belum ada tiket perselisihan.</div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>Kode Tiket</th>
          <th>Pesanan</th>
          <th>Masalah</th>
          <th>Status</th>
          <th>Dibuka</th>
          <th>Diperbarui</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in tickets" :key="t.id">
          <td><strong>{{ t.ticket_code }}</strong></td>
          <td>{{ t.order_code }}</td>
          <td>{{ t.issue_type }}</td>
          <td><TicketStatusChip :status="t.status" /></td>
          <td>{{ shortDate(t.created_at) }}</td>
          <td>{{ shortDate(t.updated_at) }}</td>
          <td>
            <router-link :to="{ name: 'ticket-detail', params: { id: t.id } }" class="btn-small">
              Buka
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api, { getErrorMessage } from '../../services/api'
import TicketStatusChip from '../../components/TicketStatusChip.vue'

const tickets = ref([])
const error = ref('')

function shortDate(v) {
  return new Date(v).toLocaleString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(async () => {
  try {
    const { data } = await api.get('/tickets')
    tickets.value = data
  } catch (err) {
    error.value = getErrorMessage(err)
  }
})
</script>
