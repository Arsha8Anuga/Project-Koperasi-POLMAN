<script setup lang="ts">
import { PlusIcon, ScanBarcodeIcon, SquarePenIcon } from '@lucide/vue'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ActiveBadge from '@/components/common/ActiveBadge.vue'
import BarcodeScanner from '@/components/common/BarcodeScanner.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FilterToggle from '@/components/common/FilterToggle.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import SearchInput from '@/components/common/SearchInput.vue'
import StockBadge from '@/components/common/StockBadge.vue'
import DataTable from '@/components/table/DataTable.vue'
import TablePagination from '@/components/table/TablePagination.vue'
import type { Column } from '@/components/table/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { usePagination } from '@/composables/usePagination'
import { useScannerInput } from '@/composables/useScannerInput'
import { useToast } from '@/composables/useToast'
import { categoryApi, productApi } from '@/services/api'
import { ApiException, errorMessage } from '@/services/apiClient'
import type { Category, Product, StockStatus } from '@/types/api'
import { formatRupiah } from '@/utils/format'

const toast = useToast()
const router = useRouter()
const categories = ref<Category[]>([])

const list = usePagination<
  Product,
  { search: string; categoryId: string; stockStatus: StockStatus | ''; isActive: boolean | ''; sort: 'name' | 'stock' | '-stock' | '-createdAt' }
>((q) => productApi.list(q), { search: '', categoryId: '', stockStatus: '', isActive: '', sort: 'name' })

onMounted(async () => {
  list.load()
  categories.value = await categoryApi.list().catch(() => [])
})

const activeOptions: { value: boolean | ''; label: string }[] = [
  { value: '', label: 'Semua' },
  { value: true, label: 'Aktif' },
  { value: false, label: 'Nonaktif' },
]

const columns: Column[] = [
  { key: 'name', label: 'Produk' },
  { key: 'categoryName', label: 'Kategori' },
  { key: 'sellingPrice', label: 'Harga jual', align: 'right' },
  { key: 'costPrice', label: 'HPP', align: 'right' },
  { key: 'stock', label: 'Stok', align: 'right' },
  { key: 'isActive', label: 'Status' },
  { key: 'actions', label: '', align: 'right' },
]

// ---------- barcode: scan barang di tangan → buka produknya (cek harga/stok) ----------
const scanOpen = ref(false)

async function openByCode(raw: string) {
  const code = raw.trim()
  if (!code) return
  try {
    const p = await productApi.lookup(code)
    router.push({ name: 'product-edit', params: { id: p.id } })
  } catch (e) {
    if (e instanceof ApiException && e.status === 404) {
      toast.error(`Barcode ${code} belum terdaftar — form produk baru dibuka dengan barcode terisi`)
      router.push({ name: 'product-new', query: { barcode: code } })
    } else toast.error(errorMessage(e, 'Gagal mencari produk'))
  }
}

useScannerInput(openByCode)

const target = ref<Product | null>(null)
const toggling = ref(false)
async function toggle() {
  if (!target.value) return
  toggling.value = true
  try {
    const p = await productApi.setStatus(target.value.id, !target.value.isActive)
    toast.success(`${p.name} ${p.isActive ? 'diaktifkan' : 'dinonaktifkan'}`)
    target.value = null
    list.reload()
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    toggling.value = false
  }
}
</script>

<template>
  <PageHeader title="Produk" subtitle="Stok hanya bertambah lewat restock dan berkurang lewat penjualan.">
    <Button as-child>
      <RouterLink :to="{ name: 'product-new' }"><PlusIcon /> Produk baru</RouterLink>
    </Button>
  </PageHeader>

  <Card class="gap-0 overflow-hidden py-0">
    <div class="flex flex-wrap items-center gap-2 border-b p-4">
      <SearchInput v-model="list.filters.search" placeholder="Cari nama, SKU, atau barcode" />
      <Button variant="outline" title="Scan barcode untuk membuka produk" @click="scanOpen = true">
        <ScanBarcodeIcon /> <span class="hidden sm:inline">Scan</span>
      </Button>
      <NativeSelect v-model="list.filters.categoryId" aria-label="Kategori">
        <NativeSelectOption value="">Semua kategori</NativeSelectOption>
        <NativeSelectOption v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</NativeSelectOption>
      </NativeSelect>
      <NativeSelect v-model="list.filters.stockStatus" aria-label="Status stok">
        <NativeSelectOption value="">Semua stok</NativeSelectOption>
        <NativeSelectOption value="OK">Aman</NativeSelectOption>
        <NativeSelectOption value="LOW">Menipis</NativeSelectOption>
        <NativeSelectOption value="OUT">Habis</NativeSelectOption>
      </NativeSelect>
      <NativeSelect v-model="list.filters.sort" aria-label="Urutkan">
        <NativeSelectOption value="name">Nama A–Z</NativeSelectOption>
        <NativeSelectOption value="stock">Stok terkecil</NativeSelectOption>
        <NativeSelectOption value="-stock">Stok terbanyak</NativeSelectOption>
        <NativeSelectOption value="-createdAt">Terbaru</NativeSelectOption>
      </NativeSelect>
      <FilterToggle v-model="list.filters.isActive" :options="activeOptions" label="Status produk" />
    </div>

    <ErrorAlert v-if="list.error.value" :message="list.error.value" class="m-4 w-auto" />

    <DataTable :columns="columns" :rows="list.rows.value" :loading="list.loading.value" row-key="id" empty="Belum ada produk">
      <template #cell-name="{ row }">
        <p class="font-semibold">{{ row.name }}</p>
        <p class="font-mono text-xs text-muted-foreground">
          {{ row.sku }}<template v-if="row.barcode"> · {{ row.barcode }}</template>
        </p>
      </template>
      <template #cell-categoryName="{ row }"><span class="text-muted-foreground">{{ row.categoryName ?? '—' }}</span></template>
      <template #cell-sellingPrice="{ row }"><span class="font-semibold">{{ formatRupiah(row.sellingPrice) }}</span></template>
      <template #cell-costPrice="{ row }"><span class="text-muted-foreground">{{ formatRupiah(row.costPrice) }}</span></template>
      <template #cell-stock="{ row }">
        <div class="flex items-center justify-end gap-2">
          <span class="font-semibold">{{ row.stock }}</span>
          <StockBadge :status="row.stockStatus" />
        </div>
        <p class="text-right text-xs text-muted-foreground">min. {{ row.minimumStock }} {{ row.unit }}</p>
      </template>
      <template #cell-isActive="{ row }"><ActiveBadge :active="row.isActive" /></template>
      <template #cell-actions="{ row }">
        <div class="flex justify-end gap-1">
          <Button as-child variant="ghost" size="sm">
            <RouterLink :to="{ name: 'product-edit', params: { id: row.id } }"><SquarePenIcon /> Ubah</RouterLink>
          </Button>
          <Button variant="ghost" size="sm" :class="row.isActive && 'text-destructive hover:text-destructive'" @click="target = row">
            {{ row.isActive ? 'Nonaktifkan' : 'Aktifkan' }}
          </Button>
        </div>
      </template>
    </DataTable>
    <TablePagination v-model="list.page.value" :meta="list.meta.value" :loading="list.loading.value" />
  </Card>

  <ConfirmModal
    :open="!!target"
    :title="target?.isActive ? 'Nonaktifkan produk?' : 'Aktifkan produk?'"
    :message="
      target?.isActive
        ? `${target?.name} tidak akan muncul di aplikasi kasir. Riwayat transaksinya tetap tersimpan.`
        : `${target?.name} akan kembali muncul di aplikasi kasir.`
    "
    :confirm-text="target?.isActive ? 'Nonaktifkan' : 'Aktifkan'"
    :danger="target?.isActive"
    :loading="toggling"
    @confirm="toggle"
    @cancel="target = null"
  />
  <BarcodeScanner v-model:open="scanOpen" title="Scan untuk membuka produk" @detected="openByCode" />
</template>
