<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { transactionApi } from '@/services/transactionApi'
import type { Transaction } from '@/types/api'
import { formatDateTime, formatRupiah } from '@/utils/format'

const transactions = ref<Transaction[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    transactions.value = await transactionApi.list({ type: 'SALE' })
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-lg font-semibold">Riwayat Transaksi</h1>

    <div class="overflow-hidden rounded-xl border bg-white">
      <table class="w-full text-sm">
        <thead class="border-b bg-gray-50 text-left text-gray-500">
          <tr>
            <th class="px-4 py-3 font-medium">Kode</th>
            <th class="px-4 py-3 font-medium">Kasir</th>
            <th class="px-4 py-3 font-medium">Waktu</th>
            <th class="px-4 py-3 font-medium">Metode</th>
            <th class="px-4 py-3 font-medium">Total</th>
            <th class="px-4 py-3 font-medium">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">Memuat data...</td>
          </tr>
          <tr v-else-if="transactions.length === 0">
            <td colspan="6" class="px-4 py-8 text-center text-gray-400">Belum ada transaksi</td>
          </tr>
          <tr v-for="t in transactions" v-else :key="t.id" class="border-b last:border-0 hover:bg-gray-50">
            <td class="px-4 py-3 font-medium">{{ t.code }}</td>
            <td class="px-4 py-3">{{ t.cashierName }}</td>
            <td class="px-4 py-3">{{ formatDateTime(t.createdAt) }}</td>
            <td class="px-4 py-3">{{ t.paymentMethod }}</td>
            <td class="px-4 py-3">{{ formatRupiah(t.total) }}</td>
            <td class="px-4 py-3">
              <RouterLink :to="`/owner/transactions/${t.id}`" class="text-blue-600 hover:underline">Detail</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>