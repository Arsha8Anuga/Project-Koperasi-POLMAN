<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { transactionApi } from '@/services/transactionApi'
import type { Transaction } from '@/types/api'
import { formatDateTime, formatRupiah } from '@/utils/format'

const route = useRoute()
const tx = ref<Transaction | null>(null)
const loading = ref(true)
const errorMsg = ref('')

onMounted(async () => {
  try {
    tx.value = await transactionApi.get(route.params.id as string)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat transaksi'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-2xl space-y-4">
    <RouterLink to="/owner/transactions" class="text-sm text-blue-600 hover:underline">← Kembali ke Riwayat</RouterLink>

    <p v-if="loading" class="text-sm text-gray-400">Memuat data...</p>
    <p v-else-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div v-else-if="tx" class="space-y-6 rounded-xl border bg-white p-6">
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-lg font-semibold">{{ tx.code }}</h1>
          <p class="text-sm text-gray-500">{{ formatDateTime(tx.createdAt) }} · Kasir: {{ tx.cashierName }}</p>
        </div>
        <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">{{ tx.paymentMethod }}</span>
      </div>

      <div class="overflow-hidden rounded-lg border">
        <table class="w-full text-sm">
          <thead class="border-b bg-gray-50 text-left text-gray-500">
            <tr>
              <th class="px-3 py-2 font-medium">Produk</th>
              <th class="px-3 py-2 font-medium">Qty</th>
              <th class="px-3 py-2 font-medium">Harga</th>
              <th class="px-3 py-2 font-medium">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in tx.items" :key="i" class="border-b last:border-0">
              <td class="px-3 py-2">{{ item.productName }}</td>
              <td class="px-3 py-2">{{ item.qty }}</td>
              <td class="px-3 py-2">{{ formatRupiah(item.price) }}</td>
              <td class="px-3 py-2">{{ formatRupiah(item.subtotal) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="space-y-1 text-sm">
        <div class="flex justify-between font-semibold">
          <span>Total</span>
          <span>{{ formatRupiah(tx.total) }}</span>
        </div>
        <div v-if="tx.paymentMethod === 'CASH'" class="flex justify-between text-gray-600">
          <span>Uang Diterima</span>
          <span>{{ formatRupiah(tx.amountPaid ?? 0) }}</span>
        </div>
        <div v-if="tx.paymentMethod === 'CASH'" class="flex justify-between text-gray-600">
          <span>Kembalian</span>
          <span>{{ formatRupiah(tx.change ?? 0) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>