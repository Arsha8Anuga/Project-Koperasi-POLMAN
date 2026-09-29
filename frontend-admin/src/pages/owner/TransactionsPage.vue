<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FilterToggle from '@/components/common/FilterToggle.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SearchInput from '@/components/common/SearchInput.vue'
import DataTable from '@/components/table/DataTable.vue'
import type { Column } from '@/components/table/types'
import TablePagination from '@/components/table/TablePagination.vue'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { usePagination } from '@/composables/usePagination'
import { transactionApi } from '@/services/api'
import type { Transaction, TransactionSummary, TransactionType } from '@/types/api'
import { formatDateTime, formatNumber, formatRupiah, todayWib } from '@/utils/format'

const router = useRouter()
const summary = ref<TransactionSummary>({ count: 0, totalSales: 0, totalRestock: 0 })

const list = usePagination<Transaction, { type: TransactionType | ''; from: string; to: string; search: string }>(
  async (q) => {
    const res = await transactionApi.list(q)
    summary.value = res.summary
    return res
  },
  { type: '', from: todayWib(-6), to: todayWib(), search: '' },
)
list.load()

const typeOptions: { value: TransactionType | ''; label: string }[] = [
  { value: '', label: 'Semua' },
  { value: 'SALE', label: 'Penjualan' },
  { value: 'RESTOCK', label: 'Restock' },
]

const columns: Column[] = [
  { key: 'code', label: 'Kode' },
  { key: 'createdAt', label: 'Waktu' },
  { key: 'type', label: 'Jenis' },
  { key: 'party', label: 'Kasir / Supplier' },
  { key: 'customer', label: 'Pelanggan' },
  { key: 'total', label: 'Total', align: 'right' },
]

function open(t: Transaction) {
  router.push({ name: 'owner-transaction-detail', params: { id: t.id } })
}
</script>

<template>
  <PageHeader title="Riwayat Transaksi" subtitle="Semua penjualan dan restock. Klik baris untuk melihat detail." />

  <div class="mb-6 grid gap-4 sm:grid-cols-3">
    <Card class="py-5">
      <CardContent class="px-5">
        <p class="text-[13px] font-semibold text-muted-foreground">Jumlah transaksi</p>
        <p class="num mt-1 text-2xl font-extrabold">{{ formatNumber(summary.count) }}</p>
      </CardContent>
    </Card>
    <Card class="py-5">
      <CardContent class="px-5">
        <p class="text-[13px] font-semibold text-muted-foreground">Total penjualan</p>
        <p class="num mt-1 text-2xl font-extrabold text-success">{{ formatRupiah(summary.totalSales) }}</p>
      </CardContent>
    </Card>
    <Card class="py-5">
      <CardContent class="px-5">
        <p class="text-[13px] font-semibold text-muted-foreground">Total restock</p>
        <p class="num mt-1 text-2xl font-extrabold">{{ formatRupiah(summary.totalRestock) }}</p>
      </CardContent>
    </Card>
  </div>

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <SearchInput v-model="list.filters.search" placeholder="Kode transaksi / nama pelanggan" />
      <FilterToggle v-model="list.filters.type" :options="typeOptions" label="Jenis transaksi" />
      <Input v-model="list.filters.from" type="date" class="w-auto" aria-label="Dari" :max="list.filters.to" />
      <span class="text-muted-foreground">–</span>
      <Input v-model="list.filters.to" type="date" class="w-auto" aria-label="Sampai" :min="list.filters.from" />
    </div>

    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />

    <DataTable
      :columns="columns"
      :rows="list.rows.value"
      :loading="list.loading.value"
      row-key="id"
      clickable
      empty="Tidak ada transaksi pada filter ini"
      @row-click="open"
    >
      <template #cell-code="{ row }"><span class="font-mono text-[13px] font-semibold">{{ row.code }}</span></template>
      <template #cell-createdAt="{ row }"><span class="text-muted-foreground">{{ formatDateTime(row.createdAt) }}</span></template>
      <template #cell-type="{ row }">
        <Badge :variant="row.type === 'SALE' ? 'success' : 'soft'">{{ row.type === 'SALE' ? 'Penjualan' : 'Restock' }}</Badge>
      </template>
      <template #cell-party="{ row }">{{ row.cashier?.name ?? row.supplier?.name ?? '—' }}</template>
      <template #cell-customer="{ row }">{{ row.member?.name ?? row.customerName ?? '—' }}</template>
      <template #cell-total="{ row }"><span class="font-semibold">{{ formatRupiah(row.total) }}</span></template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>
</template>
