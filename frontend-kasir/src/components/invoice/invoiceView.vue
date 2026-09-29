<script setup lang="ts">
import type { Transaction } from '../../types/transaction'
import { formatRupiah } from '../../utils/formatRupiah'
import { formatDateTime } from '../../utils/formatDateTime'

defineProps<{ transaction: Transaction }>()
</script>

<template>
  <div class="mx-auto w-[300px] rounded-2xl border border-slate-200 bg-white p-5 font-mono text-slate-800 shadow-sm">
    <h2 class="text-center text-base font-bold text-slate-900">Toko Koperasi</h2>
    <p class="text-center text-xs text-slate-400">{{ transaction.code }}</p>
    <p class="text-center text-xs text-slate-400">{{ formatDateTime(transaction.createdAt) }}</p>

    <p class="mt-3 text-xs text-slate-600">Kasir: {{ transaction.cashier.name }}</p>
    <p v-if="transaction.member" class="text-xs text-slate-600">
      Anggota: {{ transaction.member.name }} ({{ transaction.member.memberNumber }})
    </p>
    <p v-else-if="transaction.customerName" class="text-xs text-slate-600">
      Pelanggan: {{ transaction.customerName }}
    </p>

    <hr class="my-3 border-slate-200" />

    <div v-for="item in transaction.items" :key="item.productId" class="flex justify-between py-1 text-xs">
      <span class="text-slate-700">
        {{ item.name }}<br />
        <span class="text-slate-400">{{ item.quantity }} × {{ formatRupiah(item.price) }}</span>
      </span>
      <span class="font-medium text-slate-800">{{ formatRupiah(item.subtotal) }}</span>
    </div>

    <hr class="my-3 border-slate-200" />

    <div class="flex justify-between text-sm font-bold text-slate-900">
      <span>Total</span><span>{{ formatRupiah(transaction.total) }}</span>
    </div>
    <div class="mt-1 flex justify-between text-xs text-slate-600">
      <span>Metode</span><span>{{ transaction.payment.method }}</span>
    </div>
    <div class="flex justify-between text-xs text-slate-600">
      <span>Diterima</span><span>{{ formatRupiah(transaction.payment.amountPaid) }}</span>
    </div>
    <div v-if="transaction.payment.method === 'CASH'" class="flex justify-between text-xs text-slate-600">
      <span>Kembalian</span><span>{{ formatRupiah(transaction.payment.change) }}</span>
    </div>
  </div>
</template>