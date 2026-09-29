<script setup lang="ts">
import { PackageCheckIcon, PackageXIcon, TriangleAlertIcon } from '@lucide/vue'
import { computed, onMounted, ref, watch } from 'vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FilterToggle from '@/components/common/FilterToggle.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import StockBadge from '@/components/common/StockBadge.vue'
import ChartCard from '@/components/charts/ChartCard.vue'
import StockChart from '@/components/charts/StockChart.vue'
import DataTable from '@/components/table/DataTable.vue'
import TablePagination from '@/components/table/TablePagination.vue'
import type { Column } from '@/components/table/types'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { usePagination } from '@/composables/usePagination'
import { categoryApi, stockApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import type { Category, StockMovement, StockReport, StockStatus } from '@/types/api'
import { formatDateTime, formatNumber, todayWib } from '@/utils/format'

const tab = ref<string | number>('stock')
const categories = ref<Category[]>([])
const categoryId = ref('')
const status = ref<StockStatus | ''>('')
const report = ref<StockReport | null>(null)
const loading = ref(true)
const error = ref('')

async function loadReport() {
  loading.value = true
  error.value = ''
  try {
    report.value = await stockApi.report({ categoryId: categoryId.value, stockStatus: status.value })
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat stok')
  } finally {
    loading.value = false
  }
}
watch([categoryId, status], loadReport)

const statusOptions: { value: StockStatus | ''; label: string }[] = [
  { value: '', label: 'Semua' },
  { value: 'LOW', label: 'Menipis' },
  { value: 'OUT', label: 'Habis' },
  { value: 'OK', label: 'Aman' },
]

/** Chart: 25 produk dengan rasio stok/minimum terendah — yang paling perlu perhatian. */
const chartItems = computed(() =>
  [...(report.value?.items ?? [])]
    .sort((a, b) => a.stock / Math.max(a.minimumStock, 1) - b.stock / Math.max(b.minimumStock, 1))
    .slice(0, 25),
)

const stockColumns: Column[] = [
  { key: 'name', label: 'Produk' },
  { key: 'categoryName', label: 'Kategori' },
  { key: 'stock', label: 'Stok', align: 'right' },
  { key: 'minimumStock', label: 'Minimum', align: 'right' },
  { key: 'stockStatus', label: 'Status' },
]

const moves = usePagination<StockMovement, { type: string; from: string; to: string }>((q) => stockApi.movements(q), {
  type: '',
  from: todayWib(-6),
  to: todayWib(),
})
const moveColumns: Column[] = [
  { key: 'createdAt', label: 'Waktu' },
  { key: 'productName', label: 'Produk' },
  { key: 'type', label: 'Jenis' },
  { key: 'quantity', label: 'Perubahan', align: 'right' },
  { key: 'stockAfter', label: 'Stok akhir', align: 'right' },
  { key: 'referenceCode', label: 'Referensi' },
]
watch(tab, (t) => t === 'movements' && moves.rows.value.length === 0 && moves.load())

onMounted(async () => {
  loadReport()
  categories.value = await categoryApi.list().catch(() => [])
})
</script>

<template>
  <Tabs v-model="tab">
    <PageHeader title="Stok" subtitle="Status stok produk aktif. Menipis = stok ≤ minimum.">
      <TabsList>
        <TabsTrigger value="stock" class="px-3">Posisi stok</TabsTrigger>
        <TabsTrigger value="movements" class="px-3">Pergerakan</TabsTrigger>
      </TabsList>
    </PageHeader>

    <TabsContent value="stock">
      <div class="mb-6 grid gap-4 sm:grid-cols-3">
        <StatCard label="Aman" :value="formatNumber(report?.counts.OK)" :icon="PackageCheckIcon" tone="success" />
        <StatCard label="Menipis" :value="formatNumber(report?.counts.LOW)" :icon="TriangleAlertIcon" tone="warning" />
        <StatCard label="Habis" :value="formatNumber(report?.counts.OUT)" :icon="PackageXIcon" tone="danger" />
      </div>

      <ChartCard
        class="mb-6"
        title="Stok vs stok minimum"
        subtitle="25 produk yang paling mendekati / di bawah batas minimum"
        :loading="loading && !report"
        :error="error"
        :empty="!chartItems.length"
        :height="320"
      >
        <StockChart :items="chartItems" />
      </ChartCard>

      <Card class="gap-0 overflow-hidden py-0">
        <div class="flex flex-wrap items-center gap-2 border-b p-4">
          <NativeSelect v-model="categoryId" aria-label="Kategori">
            <NativeSelectOption value="">Semua kategori</NativeSelectOption>
            <NativeSelectOption v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</NativeSelectOption>
          </NativeSelect>
          <FilterToggle v-model="status" :options="statusOptions" label="Status stok" />
        </div>
        <DataTable :columns="stockColumns" :rows="report?.items ?? []" :loading="loading" row-key="productId" empty="Tidak ada produk">
          <template #cell-name="{ row }">
            <p class="font-semibold">{{ row.name }}</p>
            <p class="font-mono text-xs text-muted-foreground">{{ row.sku }}</p>
          </template>
          <template #cell-categoryName="{ row }"><span class="text-muted-foreground">{{ row.categoryName ?? '—' }}</span></template>
          <template #cell-stock="{ row }"><span class="font-bold">{{ row.stock }}</span></template>
          <template #cell-stockStatus="{ row }"><StockBadge :status="row.stockStatus" /></template>
        </DataTable>
      </Card>
    </TabsContent>

    <TabsContent value="movements">
      <Card class="gap-0 overflow-hidden py-0">
        <div class="flex flex-wrap items-center gap-2 border-b p-4">
          <NativeSelect v-model="moves.filters.type" aria-label="Jenis">
            <NativeSelectOption value="">Semua jenis</NativeSelectOption>
            <NativeSelectOption value="SALE">Penjualan</NativeSelectOption>
            <NativeSelectOption value="RESTOCK">Restock</NativeSelectOption>
          </NativeSelect>
          <Input v-model="moves.filters.from" type="date" class="w-auto" aria-label="Dari" :max="moves.filters.to" />
          <span class="text-muted-foreground">–</span>
          <Input v-model="moves.filters.to" type="date" class="w-auto" aria-label="Sampai" :min="moves.filters.from" />
        </div>
        <ErrorAlert v-if="moves.error.value" :message="moves.error.value" class="m-4 w-auto" />
        <DataTable
          :columns="moveColumns"
          :rows="moves.rows.value"
          :loading="moves.loading.value"
          row-key="id"
          empty="Tidak ada pergerakan stok"
        >
          <template #cell-createdAt="{ row }"><span class="text-muted-foreground">{{ formatDateTime(row.createdAt) }}</span></template>
          <template #cell-type="{ row }">
            <Badge :variant="row.type === 'SALE' ? 'outline' : 'soft'">{{ row.type === 'SALE' ? 'Penjualan' : 'Restock' }}</Badge>
          </template>
          <template #cell-quantity="{ row }">
            <span class="font-bold" :class="row.quantity < 0 ? 'text-destructive' : 'text-success'">
              {{ row.quantity > 0 ? '+' : '' }}{{ row.quantity }}
            </span>
          </template>
          <template #cell-stockAfter="{ row }">
            <span class="text-muted-foreground">{{ row.stockBefore }} → </span><strong>{{ row.stockAfter }}</strong>
          </template>
          <template #cell-referenceCode="{ row }"><span class="font-mono text-[13px]">{{ row.referenceCode }}</span></template>
        </DataTable>
        <TablePagination v-model="moves.page.value" :meta="moves.meta.value" :loading="moves.loading.value" />
      </Card>
    </TabsContent>
  </Tabs>
</template>
