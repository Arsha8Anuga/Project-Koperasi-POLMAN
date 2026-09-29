<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { Transaction } from '@/types/api'
import { formatRupiah } from '@/utils/format'

/** Rincian transaksi (SALE atau RESTOCK). Dipakai halaman detail transaksi & detail restock. */
defineProps<{ trx: Transaction }>()
</script>

<template>
  <div class="grid items-start gap-6 lg:grid-cols-[1fr_20rem]">
    <Card class="gap-0 overflow-hidden py-0">
      <Table>
        <TableHeader class="bg-muted/60">
          <TableRow class="hover:bg-transparent">
            <TableHead class="h-11 px-4">Produk</TableHead>
            <TableHead class="text-right">Qty</TableHead>
            <TableHead class="text-right">{{ trx.type === 'SALE' ? 'Harga' : 'Harga beli' }}</TableHead>
            <TableHead v-if="trx.type === 'SALE'" class="text-right">HPP</TableHead>
            <TableHead class="px-4 text-right">Subtotal</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="i in trx.items" :key="i.productId">
            <TableCell class="px-4 py-3">
              <p class="font-semibold">{{ i.name }}</p>
              <p class="font-mono text-xs text-muted-foreground">{{ i.sku }}</p>
            </TableCell>
            <TableCell class="text-right">{{ i.quantity }} <span class="text-muted-foreground">{{ i.unit }}</span></TableCell>
            <TableCell class="text-right">{{ formatRupiah(i.price ?? i.purchasePrice ?? 0) }}</TableCell>
            <TableCell v-if="trx.type === 'SALE'" class="text-right text-muted-foreground">{{ formatRupiah(i.costPrice ?? 0) }}</TableCell>
            <TableCell class="px-4 text-right font-semibold">{{ formatRupiah(i.subtotal) }}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Card>

    <Card class="py-5 text-sm">
      <CardContent class="space-y-4 px-5">
        <dl class="space-y-2.5">
          <template v-if="trx.type === 'SALE'">
            <div class="flex justify-between gap-3">
              <dt class="text-muted-foreground">Kasir</dt>
              <dd class="font-semibold">{{ trx.cashier?.name }}</dd>
            </div>
            <div class="flex justify-between gap-3">
              <dt class="text-muted-foreground">Pelanggan</dt>
              <dd class="text-right font-semibold">
                {{ trx.member?.name ?? trx.customerName ?? '—' }}
                <span v-if="trx.member" class="block font-mono text-xs font-normal text-muted-foreground">{{ trx.member.memberNumber }}</span>
              </dd>
            </div>
          </template>
          <div v-else class="flex justify-between gap-3">
            <dt class="text-muted-foreground">Supplier</dt>
            <dd class="text-right font-semibold">
              {{ trx.supplier?.name }}
              <span class="block font-mono text-xs font-normal text-muted-foreground">{{ trx.supplier?.supplierCode }}</span>
            </dd>
          </div>
          <div v-if="trx.notes" class="flex justify-between gap-3">
            <dt class="text-muted-foreground">Catatan</dt>
            <dd class="text-right">{{ trx.notes }}</dd>
          </div>
        </dl>
        <Separator />
        <div class="space-y-2">
          <div class="flex items-baseline justify-between">
            <span class="font-semibold text-muted-foreground">Total</span>
            <span class="num text-2xl font-extrabold">{{ formatRupiah(trx.total) }}</span>
          </div>
          <template v-if="trx.payment">
            <div class="flex items-center justify-between">
              <span class="text-muted-foreground">Metode</span>
              <Badge :variant="trx.payment.method === 'CASH' ? 'outline' : 'soft'">
                {{ trx.payment.method === 'CASH' ? 'Tunai' : 'QRIS' }}
              </Badge>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Dibayar</span><span class="num">{{ formatRupiah(trx.payment.amountPaid) }}</span>
            </div>
            <div v-if="trx.payment.method === 'CASH'" class="flex justify-between">
              <span class="text-muted-foreground">Kembalian</span><span class="num">{{ formatRupiah(trx.payment.change) }}</span>
            </div>
          </template>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
