<script setup lang="ts">
import type { Transaction } from '../../types/transaction'
import { formatRupiah } from '../../utils/formatRupiah'
import { formatDateTime } from '../../utils/formatDateTime'

defineProps<{ transaction: Transaction }>()
</script>

<template>
  <div class="invoice">
    <h2>Toko Koperasi</h2>
    <p class="muted">{{ transaction.code }}</p>
    <p class="muted">{{ formatDateTime(transaction.createdAt) }}</p>
    <p>Kasir: {{ transaction.cashier.name }}</p>
    <p v-if="transaction.member">
      Anggota: {{ transaction.member.name }} ({{ transaction.member.memberNumber }})
    </p>
    <p v-else-if="transaction.customerName">Pelanggan: {{ transaction.customerName }}</p>

    <hr />

    <div v-for="item in transaction.items" :key="item.productId" class="row">
      <span>{{ item.name }}<br /><small>{{ item.quantity }} × {{ formatRupiah(item.price) }}</small></span>
      <span>{{ formatRupiah(item.subtotal) }}</span>
    </div>

    <hr />

    <div class="row bold"><span>Total</span><span>{{ formatRupiah(transaction.total) }}</span></div>
    <div class="row"><span>Metode</span><span>{{ transaction.payment.method }}</span></div>
    <div class="row"><span>Diterima</span><span>{{ formatRupiah(transaction.payment.amountPaid) }}</span></div>
    <!-- Kembalian disembunyikan untuk QRIS -->
    <div v-if="transaction.payment.method === 'CASH'" class="row">
      <span>Kembalian</span><span>{{ formatRupiah(transaction.payment.change) }}</span>
    </div>
  </div>
</template>

<style scoped>
.invoice { width: 300px; margin: 0 auto; padding: 16px; font-family: monospace; }
.row { display: flex; justify-content: space-between; margin: 4px 0; }
.bold { font-weight: bold; }
.muted { color: #666; margin: 0; }
h2 { text-align: center; margin: 0 0 8px; }
</style>