<script setup lang="ts">
import type { Sale } from '@/types'
import { formatDateTime, formatRupiah } from '@/utils/format'
import { BRAND } from '@/utils/brand'

defineProps<{ sale: Sale }>()
</script>

<!-- Struk selalu hitam di atas putih (juga di mode gelap) karena ini yang dicetak/di-PDF-kan. -->
<template>
  <div class="receipt mx-auto w-[300px] rounded-xl bg-white px-5 py-6 font-mono text-[12px] leading-relaxed text-[#111827] shadow-sm">
    <div class="text-center">
      <p class="font-sans text-base font-extrabold tracking-tight uppercase">{{ BRAND.name }}</p>
      <p class="text-[11px] text-[#4b5563]">Struk Penjualan</p>
    </div>

    <div class="my-3 border-t border-dashed border-[#9ca3af]" />

    <dl class="space-y-0.5">
      <div class="flex justify-between"><dt>No.</dt><dd class="font-semibold">{{ sale.code }}</dd></div>
      <div class="flex justify-between"><dt>Waktu</dt><dd>{{ formatDateTime(sale.createdAt) }}</dd></div>
      <div class="flex justify-between"><dt>Kasir</dt><dd>{{ sale.cashier.name }}</dd></div>
      <div v-if="sale.member" class="flex justify-between">
        <dt>Anggota</dt><dd class="text-right">{{ sale.member.name }}<br />{{ sale.member.memberNumber }}</dd>
      </div>
      <div v-else-if="sale.customerName" class="flex justify-between">
        <dt>Pelanggan</dt><dd>{{ sale.customerName }}</dd>
      </div>
    </dl>

    <div class="my-3 border-t border-dashed border-[#9ca3af]" />

    <div v-for="item in sale.items" :key="item.productId" class="mb-1.5">
      <p class="font-semibold">{{ item.name }}</p>
      <div class="flex justify-between text-[#374151]">
        <span>{{ item.quantity }} {{ item.unit }} × {{ formatRupiah(item.price) }}</span>
        <span>{{ formatRupiah(item.subtotal) }}</span>
      </div>
    </div>

    <div class="my-3 border-t border-dashed border-[#9ca3af]" />

    <div class="flex justify-between text-[14px] font-bold">
      <span>TOTAL</span><span>{{ formatRupiah(sale.total) }}</span>
    </div>
    <div class="mt-1 flex justify-between">
      <span>{{ sale.payment.method === 'CASH' ? 'Tunai' : 'QRIS' }}</span><span>{{ formatRupiah(sale.payment.amountPaid) }}</span>
    </div>
    <div v-if="sale.payment.method === 'CASH'" class="flex justify-between">
      <span>Kembalian</span><span>{{ formatRupiah(sale.payment.change) }}</span>
    </div>

    <div class="my-3 border-t border-dashed border-[#9ca3af]" />
    <p class="text-center text-[11px] text-[#4b5563]">Terima kasih atas kunjungannya</p>
  </div>
</template>
