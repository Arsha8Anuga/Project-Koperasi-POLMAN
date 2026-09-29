<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { restockApi } from '@/services/restockApi'
import type { Restock } from '@/types/api'
import { formatDateTime, formatRupiah } from '@/utils/format'

const restocks = ref<Restock[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    restocks.value = await restockApi.list()
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h1 class="text-lg font-semibold">Restock</h1>
      <RouterLink to="/logistik/restocks/new" class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
        + Restock Baru
      </RouterLink>
    </div>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Kode</th>
            <th class="px-4 py-3 font-medium">Supplier</th>
            <th class="px-4 py-3 font-medium">Tanggal</th>
            <th class="px-4 py-3 font-medium">Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="4" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="restocks.length === 0">
            <td colspan="4" class="px-4 py-8 text-center text-gray-400">Belum ada riwayat restock</td>
          </tr>
          <tr v-for="r in restocks" v-else :key="r.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ r.code }}</td>
            <td class="px-4 py-3">{{ r.supplierName }}</td>
            <td class="px-4 py-3">{{ formatDateTime(r.createdAt) }}</td>
            <td class="px-4 py-3">{{ formatRupiah(r.total) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>