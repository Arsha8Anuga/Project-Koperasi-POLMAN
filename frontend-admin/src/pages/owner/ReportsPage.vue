<script setup lang="ts">
import { reactive } from 'vue'
import PageHeader from '@/components/common/PageHeader.vue'
import BestSellerChart from '@/components/charts/BestSellerChart.vue'
import CashflowChart from '@/components/charts/CashflowChart.vue'
import ChartCard from '@/components/charts/ChartCard.vue'
import GrossProfitChart from '@/components/charts/GrossProfitChart.vue'
import PeriodPicker from '@/components/charts/PeriodPicker.vue'
import AssociationRulesCard from '@/components/insights/AssociationRulesCard.vue'
import '@/components/charts/setup'
import { reportApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import type { BestSellerReport, CashflowReport, GrossProfitReport, ReportPeriod } from '@/types/api'
import { formatRupiah } from '@/utils/format'

interface Slot<T> {
  data: T | null
  loading: boolean
  error: string
}
const cash = reactive<Slot<CashflowReport>>({ data: null, loading: true, error: '' })
const profit = reactive<Slot<GrossProfitReport>>({ data: null, loading: true, error: '' })
const best = reactive<Slot<BestSellerReport>>({ data: null, loading: true, error: '' })

async function fill<T>(slot: Slot<T>, fn: () => Promise<T>) {
  slot.loading = true
  slot.error = ''
  try {
    slot.data = await fn()
  } catch (e) {
    slot.error = errorMessage(e, 'Gagal memuat laporan')
  } finally {
    slot.loading = false
  }
}

function load(p: ReportPeriod) {
  fill(cash, () => reportApi.cashflow(p))
  fill(profit, () => reportApi.grossProfit(p))
  fill(best, () => reportApi.bestSellers({ from: p.from, to: p.to, limit: 10 }))
}

/** Semua bucket bernilai 0 → tampilkan "belum ada data" alih-alih grafik datar. */
const isEmpty = (buckets: object[] | undefined, keys: string[]) =>
  !buckets || buckets.every((b) => keys.every((k) => !(b as Record<string, unknown>)[k]))
</script>

<template>
  <PageHeader title="Laporan" subtitle="Arus kas ≠ laba. Arus kas = uang masuk − uang keluar; laba kotor = penjualan − HPP.">
    <PeriodPicker @change="load" />
  </PageHeader>

  <div class="grid gap-6 xl:grid-cols-2">
    <ChartCard
      title="Arus kas"
      subtitle="Pemasukan penjualan vs pengeluaran restock"
      :loading="cash.loading"
      :error="cash.error"
      :empty="isEmpty(cash.data?.buckets, ['income', 'expense'])"
    >
      <template v-if="cash.data" #summary>
        <div class="grid grid-cols-3 gap-3 rounded-lg bg-muted/50 p-3 text-sm">
          <div><p class="text-muted-foreground">Masuk</p><p class="num font-bold">{{ formatRupiah(cash.data.totals.income) }}</p></div>
          <div><p class="text-muted-foreground">Keluar</p><p class="num font-bold">{{ formatRupiah(cash.data.totals.expense) }}</p></div>
          <div>
            <p class="text-muted-foreground">Bersih</p>
            <p class="num font-bold" :class="cash.data.totals.net >= 0 ? 'text-success' : 'text-destructive'">{{ formatRupiah(cash.data.totals.net) }}</p>
          </div>
        </div>
      </template>
      <CashflowChart v-if="cash.data" :report="cash.data" />
    </ChartCard>

    <ChartCard
      title="Laba kotor"
      subtitle="Pendapatan dikurangi HPP (moving average) barang yang terjual"
      :loading="profit.loading"
      :error="profit.error"
      :empty="isEmpty(profit.data?.buckets, ['revenue'])"
    >
      <template v-if="profit.data" #summary>
        <div class="grid grid-cols-3 gap-3 rounded-lg bg-muted/50 p-3 text-sm">
          <div><p class="text-muted-foreground">Pendapatan</p><p class="num font-bold">{{ formatRupiah(profit.data.totals.revenue) }}</p></div>
          <div><p class="text-muted-foreground">Laba kotor</p><p class="num font-bold text-success">{{ formatRupiah(profit.data.totals.grossProfit) }}</p></div>
          <div><p class="text-muted-foreground">Margin</p><p class="num font-bold">{{ (profit.data.totals.margin * 100).toFixed(1) }}%</p></div>
        </div>
      </template>
      <GrossProfitChart v-if="profit.data" :report="profit.data" />
    </ChartCard>

    <ChartCard
      class="xl:col-span-2"
      title="Produk terlaris"
      subtitle="10 produk dengan jumlah terjual terbanyak pada periode ini"
      :loading="best.loading"
      :error="best.error"
      :empty="!best.data?.items.length"
      :height="380"
    >
      <BestSellerChart v-if="best.data" :report="best.data" />
    </ChartCard>
    <AssociationRulesCard class="xl:col-span-2" />
  </div>
</template>
