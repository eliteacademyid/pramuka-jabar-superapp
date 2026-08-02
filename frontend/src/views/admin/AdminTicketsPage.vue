<template>
  <div>
    <h2>Perselisihan (Tiket)</h2>

    <div class="row" style="display: flex; gap: 1rem; margin: 1rem 0; align-items: center">
      <select v-model="statusFilter" @change="load" style="max-width: 220px">
        <option value="">Semua status</option>
        <option value="open">Dibuka</option>
        <option value="in_review">Ditinjau</option>
        <option value="resolved">Diselesaikan</option>
        <option value="closed">Ditutup</option>
      </select>
    </div>

    <div v-if="!tickets.length" class="empty-row">Belum ada tiket.</div>

    <table v-else class="data-table">
      <thead>
        <tr>
          <th>Kode</th>
          <th>Pesanan</th>
          <th>Masalah</th>
          <th>Pembuka</th>
          <th>Toko</th>
          <th>Status</th>
          <th>Dibuka</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in tickets" :key="t.id">
          <td><strong>{{ t.ticket_code }}</strong></td>
          <td>{{ t.order_code }}</td>
          <td>{{ t.issue_type }}</td>
          <td>{{ t.opened_by }}</td>
          <td>{{ t.store_name }}</td>
          <td><TicketStatusChip :status="t.status" /></td>
          <td>{{ new Date(t.created_at).toLocaleDateString('id-ID') }}</td>
          <td>
            <router-link :to="{ name: 'admin-ticket-detail', params: { id: t.id } }" class="btn-small">
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
import api from '../../services/api'
import TicketStatusChip from '../../components/TicketStatusChip.vue'

const tickets = ref([])
const statusFilter = ref('')

async function load() {
  const { data } = await api.get('/admin/tickets', {
    params: statusFilter.value ? { status: statusFilter.value } : {}
  })
  tickets.value = data
}

onMounted(load)
</script>
