<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import DataTable, { type Column } from '@/components/table/DataTable.vue'
import { usePagination } from '@/composables/usePagination'
import { productApi } from '@/services/productApi'
import type { Product } from '@/types/api'
import { formatRupiah } from '@/utils/format'

const { page, limit, search, setPage, setSearch } = usePagination()

const rows = ref<Product[]>([])
const meta = ref<{ page: number; limit: number; total: number; totalPages: number }>()
const loading = ref(false)
const errorMsg = ref('')

const columns: Column<Product>[] = [
  { key: 'sku', label: 'SKU' },
  { key: 'name', label: 'Nama' },
  { key: 'categoryName', label: 'Kategori' },
  { key: 'sellPrice', label: 'Harga Jual', render: (r) => formatRupiah(r.sellPrice) },
  { key: 'stock', label: 'Stok' },
  { key: 'stockStatus', label: 'Status' },
  { key: 'id', label: 'Aksi' },
]

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await productApi.list({ page: page.value, limit: limit.value, search: search.value })
    rows.value = res.data
    meta.value = res.meta
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal memuat produk'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch([page, limit, search], load)

function statusBadge(status: Product['stockStatus']) {
  return {
    AMAN: 'bg-green-100 text-green-700',
    MENIPIS: 'bg-yellow-100 text-yellow-700',
    HABIS: 'bg-red-100 text-red-700',
  }[status]
}
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <input
        :value="search"
        type="text"
        placeholder="Cari nama produk..."
        class="w-72 rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
        @input="setSearch(($event.target as HTMLInputElement).value)"
      />
      <RouterLink
        to="/logistik/products/new"
        class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
      >
        + Produk Baru
      </RouterLink>
    </div>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <DataTable :columns="columns" :rows="rows" :loading="loading" :meta="meta" @update:page="setPage">
      <template #cell-stockStatus="{ row }">
        <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="statusBadge(row.stockStatus)">
          {{ row.stockStatus }}
        </span>
      </template>
      <template #cell-id="{ row }">
        <RouterLink :to="`/logistik/products/${row.id}`" class="text-blue-600 hover:underline">
          Ubah
        </RouterLink>
      </template>
    </DataTable>
  </div>
</template>