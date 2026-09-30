<script setup lang="ts">
import { CircleAlertIcon, RefreshCwIcon, ScanBarcodeIcon, SearchIcon, SearchXIcon, XIcon } from '@lucide/vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import CartPanel from '@/components/cart/CartPanel.vue'
import BarcodeScanner from '@/components/common/BarcodeScanner.vue'
import ProductCard from '@/components/product/ProductCard.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Input } from '@/components/ui/input'
import { Kbd } from '@/components/ui/kbd'
import { Skeleton } from '@/components/ui/skeleton'
import { useScannerInput } from '@/composables/useScannerInput'
import { ApiException, errorMessage } from '@/services/api'
import { catalogApi } from '@/services/catalogApi'
import { useCartStore } from '@/stores/cart'
import type { Category, Product } from '@/types'
import { formatRupiah } from '@/utils/format'

const cart = useCartStore()

const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const total = ref(0)
const search = ref('')
const categoryId = ref('')
const loading = ref(true)
const error = ref('')

let requestId = 0
let loadedQuery = '' // query yang menghasilkan daftar `products` saat ini
async function loadProducts() {
  const id = ++requestId
  const query = search.value.trim()
  loading.value = true
  error.value = ''
  try {
    const res = await catalogApi.products({ search: query, categoryId: categoryId.value })
    if (id !== requestId) return // respons lama datang belakangan: abaikan
    products.value = res.data
    loadedQuery = query
    total.value = res.meta.total
    cart.sync(res.data)
  } catch (e) {
    if (id === requestId) error.value = errorMessage(e, 'Gagal memuat produk')
  } finally {
    if (id === requestId) loading.value = false
  }
}

let debounce: ReturnType<typeof setTimeout> | undefined
watch(search, () => {
  clearTimeout(debounce)
  debounce = setTimeout(loadProducts, 300)
})
watch(categoryId, loadProducts)

const qtyInCart = computed(() => new Map(cart.items.map((i) => [i.productId, i.quantity])))

// ---------- barcode: scanner USB, ketik + Enter, atau kamera ----------
const scanOpen = ref(false)
const scanning = ref(false)

function addScanned(p: Product) {
  const inCart = qtyInCart.value.get(p.id) ?? 0
  if (p.stock <= 0) return toast.error(`${p.name} stoknya habis`)
  if (inCart >= p.stock) return toast.warning(`${p.name}: sudah maksimal sesuai stok (${p.stock})`)
  cart.add(p)
  toast.success(`+1 ${p.name}`, { duration: 1500 })
}

/** Kode dari scanner/kamera/Enter. Cocok persis barcode/SKU → langsung masuk keranjang. */
async function handleCode(raw: string) {
  const code = raw.trim()
  if (!code || scanning.value) return
  const local = products.value.find((p) => p.barcode === code || p.sku === code.toUpperCase())
  if (local) return addScanned(local)
  scanning.value = true
  try {
    addScanned(await catalogApi.lookup(code))
  } catch (e) {
    if (e instanceof ApiException && e.status === 404) toast.error(errorMessage(e, `Kode ${code} belum terdaftar`))
    else toast.error(errorMessage(e, 'Gagal mencari produk'))
  } finally {
    scanning.value = false
  }
}

/** Enter di kolom pencarian: barcode/SKU persis → tambah; kalau hasil pencarian tinggal satu → tambah juga. */
async function onSearchEnter() {
  const code = search.value.trim()
  if (!code) return
  const exact = products.value.find((p) => p.barcode === code || p.sku === code.toUpperCase())
  if (exact) {
    addScanned(exact)
    search.value = ''
    return
  }
  // hanya kalau daftar yang tampil memang hasil dari teks yang sedang diketik
  if (!loading.value && loadedQuery === code && products.value.length === 1 && products.value[0]) {
    addScanned(products.value[0])
    search.value = ''
    return
  }
  // tidak ada di katalog yang sedang tampil (mis. hasil dibatasi 100): tanya backend
  if (/^[0-9A-Za-z-]{4,}$/.test(code)) {
    await handleCode(code)
    search.value = ''
  }
}

useScannerInput(handleCode)

function focusSearch() {
  document.getElementById('product-search')?.focus()
}

// Ketik "/" di mana saja untuk langsung ke kolom pencarian.
function onKey(e: KeyboardEvent) {
  const target = e.target as HTMLElement
  if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) {
    e.preventDefault()
    focusSearch()
  }
}

function resetFilter() {
  search.value = ''
  categoryId.value = ''
}

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  focusSearch()
  loadProducts()
  try {
    categories.value = await catalogApi.categories()
  } catch {
    /* filter kategori opsional: katalog tetap bisa dipakai */
  }
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  clearTimeout(debounce)
})
</script>

<template>
  <div class="flex h-full">
    <section class="flex min-w-0 flex-1 flex-col">
      <div class="space-y-3 border-b bg-card/60 px-4 py-4 backdrop-blur sm:px-6">
        <div class="relative">
          <SearchIcon class="pointer-events-none absolute top-1/2 left-3.5 size-[18px] -translate-y-1/2 text-muted-foreground" />
          <Input
            id="product-search"
            v-model="search"
            data-scan-input
            class="h-11 pr-24 pl-11 text-[15px] md:text-[15px]"
            placeholder="Cari nama/SKU, atau scan barcode lalu Enter…"
            aria-label="Cari produk atau scan barcode"
            @keydown.enter.prevent="onSearchEnter"
          />
          <div class="absolute top-1/2 right-1.5 flex -translate-y-1/2 items-center gap-1">
            <Button v-if="search" variant="ghost" size="icon-sm" aria-label="Hapus pencarian" @click="search = ''">
              <XIcon />
            </Button>
            <Kbd v-else class="hidden sm:inline-flex">/</Kbd>
            <Button variant="ghost" size="icon-sm" title="Scan pakai kamera" aria-label="Scan pakai kamera" @click="scanOpen = true">
              <ScanBarcodeIcon />
            </Button>
          </div>
        </div>

        <div class="flex gap-2 overflow-x-auto pb-0.5">
          <Button size="sm" class="shrink-0 rounded-full" :variant="categoryId === '' ? 'default' : 'outline'" @click="categoryId = ''">
            Semua
          </Button>
          <Button
            v-for="c in categories"
            :key="c.id"
            size="sm"
            class="shrink-0 rounded-full"
            :variant="categoryId === c.id ? 'default' : 'outline'"
            @click="categoryId = c.id"
          >
            {{ c.name }}
          </Button>
        </div>
      </div>

      <main class="flex-1 overflow-y-auto px-4 py-5 sm:px-6">
        <div class="mb-4 flex items-center justify-between">
          <p class="text-sm text-muted-foreground">
            <span class="num font-semibold text-foreground">{{ total }}</span> produk
            <span v-if="total > products.length">(menampilkan {{ products.length }} — persempit pencarian)</span>
          </p>
          <Button variant="ghost" size="sm" :disabled="loading" @click="loadProducts">
            <RefreshCwIcon :class="loading && 'animate-spin'" /> Muat ulang
          </Button>
        </div>

        <Alert v-if="error" variant="destructive" class="mb-4">
          <CircleAlertIcon />
          <AlertDescription class="flex flex-wrap items-center justify-between gap-2">
            {{ error }}
            <Button variant="outline" size="xs" @click="loadProducts">Coba lagi</Button>
          </AlertDescription>
        </Alert>

        <div v-if="loading && products.length === 0" class="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
          <Skeleton v-for="n in 10" :key="n" class="h-56 rounded-xl" />
        </div>

        <div
          v-else-if="products.length > 0"
          class="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5"
          :class="loading && 'opacity-60'"
        >
          <ProductCard
            v-for="p in products"
            :key="p.id"
            :product="p"
            :in-cart="qtyInCart.get(p.id) ?? 0"
            @add="cart.add"
          />
        </div>

        <Empty v-else-if="!error" class="h-72">
          <EmptyHeader>
            <EmptyMedia variant="icon"><SearchXIcon /></EmptyMedia>
            <EmptyTitle>Produk tidak ditemukan</EmptyTitle>
            <EmptyDescription>Coba kata kunci atau kategori lain.</EmptyDescription>
          </EmptyHeader>
          <EmptyContent>
            <Button variant="outline" size="sm" @click="resetFilter">Reset filter</Button>
          </EmptyContent>
        </Empty>
      </main>

      <!-- Layar kecil: keranjang tersembunyi, tampilkan ringkasan + tombol bayar -->
      <div class="flex items-center justify-between gap-3 border-t bg-card px-4 py-3 lg:hidden">
        <div>
          <p class="text-xs text-muted-foreground">{{ cart.totalQty }} barang</p>
          <p class="num text-lg font-bold">{{ formatRupiah(cart.totalAmount) }}</p>
        </div>
        <Button as-child size="lg" :class="cart.isEmpty && 'pointer-events-none opacity-50'">
          <RouterLink :to="{ name: 'payment' }">Bayar</RouterLink>
        </Button>
      </div>
    </section>

    <aside class="hidden w-[22rem] shrink-0 border-l bg-card lg:block xl:w-[24rem]">
      <CartPanel />
    </aside>
  </div>

  <BarcodeScanner v-model:open="scanOpen" title="Scan barang ke keranjang" continuous @detected="handleCode" />
</template>
