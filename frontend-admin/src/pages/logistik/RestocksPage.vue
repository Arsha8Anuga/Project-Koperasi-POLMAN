<script setup lang="ts">
import { PlusIcon } from '@lucide/vue'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import DataTable from '@/components/table/DataTable.vue'
import TablePagination from '@/components/table/TablePagination.vue'
import type { Column } from '@/components/table/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { usePagination } from '@/composables/usePagination'
import { restockApi, supplierApi } from '@/services/api'
import type { Supplier, Transaction } from '@/types/api'
import { formatDateTime, formatRupiah, todayWib } from '@/utils/format'

const router = useRouter()
const suppliers = ref<Supplier[]>([])
const list = usePagination<Transaction, { supplierId: string; from: string; to: string }>((q) => restockApi.list(q), {
  supplierId: '',
  from: todayWib(-29),
  to: todayWib(),
})

onMounted(async () => {
  list.load()
  suppliers.value = await supplierApi
    .list({ limit: 100 })
    .then((r) => r.data)
    .catch(() => [])
})

function open(r: Transaction) {
  router.push({ name: 'restock-detail', params: { id: r.id } })
}

const columns: Column[] = [
  { key: 'code', label: 'Kode' },
  { key: 'createdAt', label: 'Waktu' },
  { key: 'supplier', label: 'Supplier' },
  { key: 'items', label: 'Item', align: 'right' },
  { key: 'total', label: 'Total', align: 'right' },
]
</script>

<template>
  <PageHeader title="Restock" subtitle="Setiap restock menambah stok dan menghitung ulang HPP (rata-rata bergerak).">
    <Button as-child>
      <RouterLink :to="{ name: 'restock-new' }"><PlusIcon /> Restock baru</RouterLink>
    </Button>
  </PageHeader>

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <NativeSelect v-model="list.filters.supplierId" class="min-w-48" aria-label="Supplier">
        <NativeSelectOption value="">Semua supplier</NativeSelectOption>
        <NativeSelectOption v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</NativeSelectOption>
      </NativeSelect>
      <Input v-model="list.filters.from" type="date" class="w-auto" aria-label="Dari" :max="list.filters.to" />
      <span class="text-muted-foreground">–</span>
      <Input v-model="list.filters.to" type="date" class="w-auto" aria-label="Sampai" :min="list.filters.from" />
    </div>
    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />
    <DataTable
      :columns="columns"
      :rows="list.rows.value"
      :start-index="(list.meta.value.page - 1) * list.meta.value.limit"
      :loading="list.loading.value"
      row-key="id"
      clickable
      empty="Belum ada restock pada rentang ini"
      @row-click="open"
    >
      <template #cell-code="{ row }"><span class="font-mono text-[13px] font-semibold">{{ row.code }}</span></template>
      <template #cell-createdAt="{ row }"><span class="text-muted-foreground">{{ formatDateTime(row.createdAt) }}</span></template>
      <template #cell-supplier="{ row }">{{ row.supplier?.name }}</template>
      <template #cell-items="{ row }">{{ row.items.length }} produk</template>
      <template #cell-total="{ row }"><span class="font-semibold">{{ formatRupiah(row.total) }}</span></template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>
</template>
