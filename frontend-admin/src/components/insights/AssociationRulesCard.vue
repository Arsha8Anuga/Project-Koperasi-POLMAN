<script setup lang="ts">
import { ArrowRightIcon, SparklesIcon } from '@lucide/vue'
import { onMounted, ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { insightApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import type { AssociationRules } from '@/types/api'
import { formatDateTime, formatNumber } from '@/utils/format'
import { percent } from '@/utils/insight'

/** Hasil association rules (Apriori) untuk owner: bahan paket bundling & penataan rak. */
const result = ref<AssociationRules | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    result.value = await insightApi.associationRules({ limit: 12, minLift: 1.2 })
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat analisis')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <Card class="gap-0 overflow-hidden pb-0">
    <CardHeader class="border-b pb-4!">
      <CardTitle class="flex items-center gap-2 text-base"><SparklesIcon class="size-4 text-accent-foreground" /> Sering dibeli bersama</CardTitle>
      <CardDescription>
        Association rules (Apriori) dari riwayat penjualan. <strong>Keyakinan</strong> = dari pembeli produk kiri, berapa
        persen juga membeli produk kanan. <strong>Lift</strong> &gt; 1 = lebih sering bersama daripada kebetulan.
        <template v-if="result?.meta">
          <br />Dihitung {{ formatDateTime(result.meta.generatedAt) }} dari
          {{ formatNumber(Number(result.meta.stats.transactions ?? 0)) }} transaksi.
        </template>
      </CardDescription>
    </CardHeader>
    <CardContent class="px-0">
      <div v-if="loading" class="space-y-2 p-4"><Skeleton v-for="n in 4" :key="n" class="h-8" /></div>
      <p v-else-if="error" class="p-4 text-sm text-destructive">{{ error }}</p>
      <Empty v-else-if="!result?.rules.length" class="py-10">
        <EmptyHeader>
          <EmptyMedia variant="icon"><SparklesIcon /></EmptyMedia>
          <EmptyTitle>Belum ada pola</EmptyTitle>
          <EmptyDescription>AI engine belum menghitung, atau transaksi belum cukup untuk menemukan pola.</EmptyDescription>
        </EmptyHeader>
      </Empty>
      <Table v-else>
        <TableHeader class="bg-muted/60">
          <TableRow class="hover:bg-transparent">
            <TableHead class="px-4">Kalau membeli</TableHead>
            <TableHead />
            <TableHead>Sering juga membeli</TableHead>
            <TableHead class="text-right">Keyakinan</TableHead>
            <TableHead class="text-right">Lift</TableHead>
            <TableHead class="px-4 text-right">Transaksi</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="(r, i) in result.rules" :key="i">
            <TableCell class="px-4 font-medium whitespace-normal">{{ r.antecedent.map((p) => p.name).join(' + ') }}</TableCell>
            <TableCell class="w-6 text-muted-foreground"><ArrowRightIcon class="size-4" /></TableCell>
            <TableCell class="font-medium whitespace-normal">{{ r.consequent.map((p) => p.name).join(' + ') }}</TableCell>
            <TableCell class="text-right">
              <div class="flex items-center justify-end gap-2">
                <div class="hidden h-1.5 w-16 overflow-hidden rounded-full bg-muted sm:block">
                  <div class="h-full rounded-full bg-primary" :style="{ width: `${Math.round(r.confidence * 100)}%` }" />
                </div>
                <span class="num w-10 font-semibold">{{ percent(r.confidence) }}</span>
              </div>
            </TableCell>
            <TableCell class="num text-right">{{ r.lift.toLocaleString('id-ID', { maximumFractionDigits: 1 }) }}×</TableCell>
            <TableCell class="num px-4 text-right text-muted-foreground">{{ r.count }}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </CardContent>
  </Card>
</template>
