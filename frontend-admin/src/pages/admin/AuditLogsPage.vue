<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { auditApi } from '@/services/auditApi'
import type { AuditLog } from '@/types/api'
import { formatDateTime } from '@/utils/format'

const logs = ref<AuditLog[]>([])
const loading = ref(false)

const filters = reactive({ userName: '', entity: '' })
const entities = ['Product', 'Category', 'Supplier', 'User', 'Member', 'Transaction']

let debounceTimer: ReturnType<typeof setTimeout>
async function load() {
  loading.value = true
  try {
    logs.value = await auditApi.list({ userName: filters.userName || undefined, entity: filters.entity || undefined })
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(
  () => filters.userName,
  () => {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(load, 300)
  },
)
watch(() => filters.entity, load)

function actionColor(action: string) {
  if (action.includes('DELETE') || action.includes('DEACTIVATE')) return 'text-red-600'
  if (action.includes('CREATE')) return 'text-green-600'
  return 'text-blue-600'
}
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-lg font-semibold">Audit Trail</h1>

    <div class="flex gap-3">
      <input
        v-model="filters.userName"
        type="text"
        placeholder="Cari nama user..."
        class="w-64 rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
      />
      <select v-model="filters.entity" class="rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500">
        <option value="">Semua entitas</option>
        <option v-for="e in entities" :key="e" :value="e">{{ e }}</option>
      </select>
    </div>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Waktu</th>
            <th class="px-4 py-3 font-medium">User</th>
            <th class="px-4 py-3 font-medium">Role</th>
            <th class="px-4 py-3 font-medium">Aksi</th>
            <th class="px-4 py-3 font-medium">Entitas</th>
            <th class="px-4 py-3 font-medium">Detail</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="logs.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">Tidak ada log yang cocok</td>
          </tr>
          <tr v-for="l in logs" v-else :key="l.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3">{{ formatDateTime(l.createdAt) }}</td>
            <td class="px-4 py-3">{{ l.userName }}</td>
            <td class="px-4 py-3">
              <span class="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">{{ l.userRole }}</span>
            </td>
            <td class="px-4 py-3 font-medium" :class="actionColor(l.action)">{{ l.action }}</td>
            <td class="px-4 py-3">{{ l.entity }}</td>
            <td class="px-4 py-3 text-gray-600">{{ l.detail || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>