<script setup lang="ts">
import { ArrowLeftIcon, PlusIcon, TrashIcon } from '@lucide/vue'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import ErrorAlert from '@/components/common/ErrorAlert.vue'
import FormField from '@/components/form/FormField.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardAction, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { NativeSelect, NativeSelectOption } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { productApi, restockApi, supplierApi } from '@/services/api'
import { errorMessage } from '@/services/apiClient'
import { useToast } from '@/composables/useToast'
import type { Product, Supplier } from '@/types/api'
import { formatRupiah } from '@/utils/format'

const router = useRouter()
const toast = useToast()

const suppliers = ref<Supplier[]>([])
const products = ref<Product[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const supplierId = ref('')
const notes = ref('')

interface Row {
  key: number
  productId: string
  quantity: number
  purchasePrice: number
}
let seq = 0
const rows = reactive<Row[]>([{ key: seq++, productId: '', quantity: 1, purchasePrice: 0 }])

const byId = computed(() => new Map(products.value.map((p) => [p.id, p])))
const used = computed(() => new Set(rows.map((r) => r.productId).filter(Boolean)))
const options = (row: Row) => products.value.filter((p) => p.id === row.productId || !used.value.has(p.id))
const total = computed(() => rows.reduce((n, r) => n + (r.quantity || 0) * (r.purchasePrice || 0), 0))

function onPick(row: Row, value: unknown) {
  row.productId = String(value ?? '')
  const p = byId.value.get(row.productId)
  if (p && !row.purchasePrice) row.purchasePrice = p.lastPurchasePrice || p.costPrice
}

function addRow() {
  if (rows.length < 50) rows.push({ key: seq++, productId: '', quantity: 1, purchasePrice: 0 })
}

async function loadProducts() {
  // Maksimal 100 per halaman; ambil semua halaman supaya semua produk bisa dipilih.
  const all: Product[] = []
  for (let page = 1; page <= 20; page++) {
    const res = await productApi.list({ page, limit: 100, sort: 'name' })
    all.push(...res.data)
    if (page >= res.meta.totalPages) break
  }
  products.value = all
}

onMounted(async () => {
  try {
    const [s] = await Promise.all([supplierApi.list({ limit: 100, isActive: true }), loadProducts()])
    suppliers.value = s.data
  } catch (e) {
    error.value = errorMessage(e, 'Gagal memuat data')
  } finally {
    loading.value = false
  }
})

async function submit() {
  error.value = ''
  const items = rows.filter((r) => r.productId)
  if (!supplierId.value) return (error.value = 'Pilih supplier terlebih dahulu')
  if (!items.length) return (error.value = 'Tambahkan minimal satu produk')
  if (items.some((r) => !Number.isInteger(r.quantity) || r.quantity < 1 || r.quantity > 10000))
    return (error.value = 'Jumlah tiap produk harus bilangan bulat 1–10.000')
  if (items.some((r) => !Number.isInteger(r.purchasePrice) || r.purchasePrice < 0))
    return (error.value = 'Harga beli harus bilangan bulat ≥ 0')

  saving.value = true
  try {
    const trx = await restockApi.create({
      supplierId: supplierId.value,
      notes: notes.value.trim() || null,
      items: items.map(({ productId, quantity, purchasePrice }) => ({ productId, quantity, purchasePrice })),
    })
    toast.success(`Restock ${trx.code} tersimpan`)
    router.push({ name: 'restock-detail', params: { id: trx.id } })
  } catch (e) {
    error.value = errorMessage(e, 'Gagal menyimpan restock')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Button as-child variant="ghost" size="sm" class="mb-4 -ml-2">
    <RouterLink :to="{ name: 'restocks' }"><ArrowLeftIcon /> Restock</RouterLink>
  </Button>
  <h1 class="text-2xl font-bold tracking-tight">Restock baru</h1>
  <p class="mt-1 mb-6 text-sm text-muted-foreground">Stok bertambah dan HPP dihitung ulang otomatis setelah disimpan.</p>

  <div v-if="loading" class="space-y-6">
    <Skeleton class="h-32 rounded-xl" />
    <Skeleton class="h-64 rounded-xl" />
  </div>

  <form v-else class="space-y-6" @submit.prevent="submit">
    <ErrorAlert v-if="error" :message="error" />

    <Card>
      <CardContent class="grid gap-5 sm:grid-cols-2">
        <FormField label="Supplier" for="supplier" required>
          <NativeSelect id="supplier" v-model="supplierId" class="w-full">
            <NativeSelectOption value="" disabled>Pilih supplier aktif</NativeSelectOption>
            <NativeSelectOption v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }} ({{ s.supplierCode }})</NativeSelectOption>
          </NativeSelect>
        </FormField>
        <FormField label="Catatan" for="notes" hint="Opsional, misalnya nomor faktur">
          <Input id="notes" v-model="notes" maxlength="300" />
        </FormField>
      </CardContent>
    </Card>

    <Card class="gap-0 overflow-hidden py-0">
      <CardHeader class="border-b pt-4 pb-4!">
        <CardTitle class="flex items-center gap-2 text-base">Produk <Badge variant="soft">{{ rows.length }}</Badge></CardTitle>
        <CardAction>
          <Button type="button" variant="secondary" size="sm" :disabled="rows.length >= 50" @click="addRow"><PlusIcon /> Tambah baris</Button>
        </CardAction>
      </CardHeader>
      <Table>
        <TableHeader class="bg-muted/60">
          <TableRow class="hover:bg-transparent">
            <TableHead class="h-11 min-w-64 px-4">Produk</TableHead>
            <TableHead class="w-32">Jumlah</TableHead>
            <TableHead class="w-44">Harga beli / unit</TableHead>
            <TableHead class="w-40 text-right">Subtotal</TableHead>
            <TableHead class="w-12" />
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="(row, i) in rows" :key="row.key" class="hover:bg-transparent">
            <TableCell class="px-4 py-3 align-top whitespace-normal">
              <NativeSelect
                :model-value="row.productId"
                class="w-full"
                :aria-label="`Produk baris ${i + 1}`"
                @update:model-value="(v) => onPick(row, v)"
              >
                <NativeSelectOption value="" disabled>Pilih produk</NativeSelectOption>
                <NativeSelectOption v-for="p in options(row)" :key="p.id" :value="p.id">
                  {{ p.name }} · {{ p.sku }} (stok {{ p.stock }}){{ p.isActive ? '' : ' — nonaktif' }}
                </NativeSelectOption>
              </NativeSelect>
              <p v-if="byId.get(row.productId)" class="mt-1 text-xs text-muted-foreground">
                HPP sekarang {{ formatRupiah(byId.get(row.productId)!.costPrice) }} · beli terakhir
                {{ formatRupiah(byId.get(row.productId)!.lastPurchasePrice) }}
              </p>
            </TableCell>
            <TableCell class="py-3 align-top">
              <Input v-model.number="row.quantity" type="number" min="1" max="10000" step="1" class="num" :aria-label="`Jumlah baris ${i + 1}`" />
            </TableCell>
            <TableCell class="py-3 align-top">
              <Input v-model.number="row.purchasePrice" type="number" min="0" step="1" class="num" :aria-label="`Harga beli baris ${i + 1}`" />
            </TableCell>
            <TableCell class="py-5 text-right align-top font-semibold">
              {{ formatRupiah((row.quantity || 0) * (row.purchasePrice || 0)) }}
            </TableCell>
            <TableCell class="py-3 align-top">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                class="text-muted-foreground hover:text-destructive"
                :disabled="rows.length <= 1"
                aria-label="Hapus baris"
                @click="rows.splice(i, 1)"
              >
                <TrashIcon />
              </Button>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
      <div class="flex items-center justify-between border-t bg-muted/50 px-5 py-4">
        <span class="font-semibold text-muted-foreground">Total pembelian</span>
        <span class="num text-2xl font-extrabold">{{ formatRupiah(total) }}</span>
      </div>
    </Card>

    <div class="flex gap-2">
      <Button type="submit" :disabled="saving"><Spinner v-if="saving" /> Simpan restock</Button>
      <Button as-child variant="outline"><RouterLink :to="{ name: 'restocks' }">Batal</RouterLink></Button>
    </div>
  </form>
</template>
