<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { productApi } from '@/services/productApi'
import { restockApi } from '@/services/restockApi'
import { supplierApi } from '@/services/supplierApi'
import type { Product, Supplier } from '@/types/api'
import { formatRupiah } from '@/utils/format'

const router = useRouter()

const suppliers = ref<Supplier[]>([])
const products = ref<Product[]>([])
const loading = ref(true)
const saving = ref(false)
const errorMsg = ref('')

const supplierId = ref('')
const note = ref('')

interface Row { productId: string; qty: number; purchasePrice: number }
const items = reactive<Row[]>([{ productId: '', qty: 1, purchasePrice: 0 }])

const usedProductIds = computed(() => new Set(items.map((r) => r.productId).filter(Boolean)))

function availableFor(row: Row): Product[] {
  return products.value.filter((p) => p.id === row.productId || !usedProductIds.value.has(p.id))
}

function onProductChange(row: Row) {
  const p = products.value.find((x) => x.id === row.productId)
  row.purchasePrice = p?.lastPurchasePrice ?? 0
}

function addRow() {
  items.push({ productId: '', qty: 1, purchasePrice: 0 })
}

function removeRow(idx: number) {
  if (items.length > 1) items.splice(idx, 1)
}

const total = computed(() => items.reduce((sum, r) => sum + r.qty * r.purchasePrice, 0))

async function submit() {
  errorMsg.value = ''
  if (!supplierId.value) {
    errorMsg.value = 'Supplier wajib dipilih'
    return
  }
  const validItems = items.filter((r) => r.productId && r.qty > 0)
  if (validItems.length === 0) {
    errorMsg.value = 'Minimal satu item produk dengan qty > 0'
    return
  }

  saving.value = true
  try {
    const supplier = suppliers.value.find((s) => s.id === supplierId.value)
    const nameMap: Record<string, string> = {}
    products.value.forEach((p) => { nameMap[p.id] = p.name })

    await restockApi.create(
      { supplierId: supplierId.value, note: note.value, items: validItems },
      supplier?.name ?? '',
      nameMap,
    )
    router.push('/logistik/restocks')
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Gagal menyimpan restock'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    ;[suppliers.value, products.value] = await Promise.all([supplierApi.list(), productApi.listAll()])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-3xl space-y-4">
    <h1 class="text-lg font-semibold">Restock Baru</h1>

    <p v-if="loading" class="text-sm text-gray-400">Memuat data...</p>

    <form v-else class="space-y-6 rounded-xl border bg-white p-6" @submit.prevent="submit">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="mb-1 block text-sm font-medium">Supplier <span class="text-red-500">*</span></label>
          <select v-model="supplierId" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500">
            <option value="" disabled>Pilih supplier</option>
            <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Catatan</label>
          <input v-model="note" type="text" class="w-full rounded-lg border px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>

      <div>
        <div class="mb-2 flex items-center justify-between">
          <label class="text-sm font-medium">Item Produk</label>
          <button type="button" class="text-sm text-blue-600 hover:underline" @click="addRow">+ Tambah baris</button>
        </div>

        <div class="overflow-hidden rounded-lg border">
          <table class="w-full text-sm">
            <thead class="border-b bg-gray-50 text-left text-gray-500">
              <tr>
                <th class="px-3 py-2 font-medium">Produk</th>
                <th class="w-24 px-3 py-2 font-medium">Qty</th>
                <th class="w-36 px-3 py-2 font-medium">Harga Beli</th>
                <th class="w-32 px-3 py-2 font-medium">Subtotal</th>
                <th class="w-10 px-3 py-2"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in items" :key="idx" class="border-b last:border-0">
                <td class="px-3 py-2">
                  <select v-model="row.productId" class="w-full rounded-lg border px-2 py-1.5 text-sm" @change="onProductChange(row)">
                    <option value="" disabled>Pilih produk</option>
                    <option v-for="p in availableFor(row)" :key="p.id" :value="p.id">{{ p.name }} ({{ p.sku }})</option>
                  </select>
                </td>
                <td class="px-3 py-2">
                  <input v-model.number="row.qty" type="number" min="1" class="w-full rounded-lg border px-2 py-1.5 text-sm" />
                </td>
                <td class="px-3 py-2">
                  <input v-model.number="row.purchasePrice" type="number" min="0" class="w-full rounded-lg border px-2 py-1.5 text-sm" />
                </td>
                <td class="px-3 py-2 text-gray-600">{{ formatRupiah(row.qty * row.purchasePrice) }}</td>
                <td class="px-3 py-2">
                  <button type="button" class="text-red-500 hover:text-red-700" :disabled="items.length <= 1" @click="removeRow(idx)">✕</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex justify-end text-sm font-semibold">
        Total: {{ formatRupiah(total) }}
      </div>

      <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

      <div class="flex gap-3">
        <button type="submit" :disabled="saving"
          class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {{ saving ? 'Menyimpan...' : 'Simpan Restock' }}
        </button>
        <RouterLink to="/logistik/restocks" class="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50">
          Batal
        </RouterLink>
      </div>
    </form>
  </div>
</template>