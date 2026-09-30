<script setup lang="ts">
import { CircleAlertIcon, RefreshCwIcon, ScanBarcodeIcon, SearchIcon, SearchXIcon, ShoppingBagIcon, XIcon } from '@lucide/vue'
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
import { Sheet, SheetContent, SheetDescription, SheetTitle } from '@/components/ui/sheet'
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

// ---------- jumlah produk per kategori (angka di tab) ----------
const counts = ref<Record<string, number>>({})
async function loadCounts() {
  try {
    const all = await catalogApi.products({ limit: 1 })
    const per = await Promise.all(categories.value.map((c) => catalogApi.products({ categoryId: c.id, limit: 1 })))
    counts.value = Object.fromEntries([['', all.meta.total], ...categories.value.map((c, i) => [c.id, per[i]?.meta.total ?? 0])])
  } catch {
    counts.value = {} // angka hanya pelengkap; tab tetap bisa dipakai
  }
}
const tabs = computed(() => [{ id: '', name: 'Semua' }, ...categories.value.map((c) => ({ id: c.id, name: c.name }))])

function reload() {
  loadProducts()
  loadCounts()
}

// ---------- HP/tablet: detail pesanan dibuka sebagai sheet dari bawah ----------
const orderOpen = ref(false)

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
    loadCounts()
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
  <div class="flex h-full gap-4 p-3 sm:p-4 lg:gap-5">
    <section class="flex min-w-0 flex-1 flex-col">
      <!-- toolbar: pencarian/scan + tab kategori -->
      <div class="flex flex-col gap-3 xl:flex-row xl:items-center">
        <div class="relative xl:w-[26rem] xl:shrink-0">
          <SearchIcon class="pointer-events-none absolute top-1/2 left-3.5 size-[18px] -translate-y-1/2 text-muted-foreground" />
          <Input
            id="product-search"
            v-model="search"
            data-scan-input
            class="h-11 rounded-xl bg-card pr-24 pl-11 text-[15px] md:text-[15px]"
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

        <div class="-mx-3 flex gap-1.5 overflow-x-auto px-3 pb-0.5 sm:mx-0 sm:px-0 xl:ml-auto" role="tablist" aria-label="Kategori">
          <button
            v-for="t in tabs"
            :key="t.id"
            type="button"
            role="tab"
            :aria-selected="categoryId === t.id"
            class="flex h-9 shrink-0 items-center gap-2 rounded-xl px-3 text-sm font-medium transition outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            :class="categoryId === t.id ? 'bg-card text-foreground shadow-sm ring-1 ring-border' : 'text-muted-foreground hover:bg-card/70 hover:text-foreground'"
            @click="categoryId = t.id"
          >
            {{ t.name }}
            <span
              v-if="counts[t.id] !== undefined"
              class="num rounded-md px-1.5 py-0.5 text-[11px] font-semibold"
              :class="categoryId === t.id ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground'"
              >{{ counts[t.id] }}</span
            >
          </button>
        </div>
      </div>

      <div class="mt-3 mb-2 flex items-center justify-between">
        <p class="text-sm text-muted-foreground">
          <span class="num font-semibold text-foreground">{{ total }}</span> produk
          <span v-if="total > products.length">(menampilkan {{ products.length }} — persempit pencarian)</span>
        </p>
        <Button variant="ghost" size="sm" :disabled="loading" @click="reload">
          <RefreshCwIcon :class="loading && 'animate-spin'" /> Muat ulang
        </Button>
      </div>

      <main class="-mx-1 flex-1 overflow-y-auto px-1 pb-4">
        <Alert v-if="error" variant="destructive" class="mb-4">
          <CircleAlertIcon />
          <AlertDescription class="flex flex-wrap items-center justify-between gap-2">
            {{ error }}
            <Button variant="outline" size="xs" @click="loadProducts">Coba lagi</Button>
          </AlertDescription>
        </Alert>

        <div v-if="loading && products.length === 0" class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          <Skeleton v-for="n in 9" :key="n" class="h-40 rounded-2xl sm:h-44" />
        </div>

        <div
          v-else-if="products.length > 0"
          class="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
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

      <!-- HP/tablet: ringkasan pesanan menempel di bawah -->
      <div class="-mx-3 -mb-3 flex items-center gap-3 border-t bg-card px-4 py-3 sm:-mx-4 sm:-mb-4 lg:hidden">
        <button type="button" class="flex min-w-0 flex-1 items-center gap-3 text-left" @click="orderOpen = true">
          <span class="relative flex size-11 shrink-0 items-center justify-center rounded-xl bg-secondary text-secondary-foreground">
            <ShoppingBagIcon class="size-5" />
            <span
              v-if="cart.totalQty"
              class="num absolute -top-1.5 -right-1.5 min-w-5 rounded-full bg-primary px-1 text-center text-[11px] leading-5 font-bold text-primary-foreground"
              >{{ cart.totalQty }}</span
            >
          </span>
          <span class="min-w-0">
            <span class="block text-xs text-muted-foreground">Lihat detail pesanan</span>
            <span class="num block text-lg leading-tight font-bold">{{ formatRupiah(cart.totalAmount) }}</span>
          </span>
        </button>
        <Button as-child size="lg" class="rounded-xl" :class="cart.isEmpty && 'pointer-events-none opacity-50'">
          <RouterLink :to="{ name: 'payment' }">Bayar</RouterLink>
        </Button>
      </div>
    </section>

    <aside class="hidden w-[23rem] shrink-0 overflow-hidden rounded-2xl border bg-card shadow-xs lg:block xl:w-[25rem]">
      <CartPanel />
    </aside>
  </div>

  <Sheet v-model:open="orderOpen">
    <SheetContent side="bottom" class="h-[88dvh] gap-0 rounded-t-2xl p-0">
      <SheetTitle class="sr-only">Detail pesanan</SheetTitle>
      <SheetDescription class="sr-only">Daftar barang di keranjang dan total pembayaran</SheetDescription>
      <CartPanel @checkout="orderOpen = false" />
    </SheetContent>
  </Sheet>

  <BarcodeScanner v-model:open="scanOpen" title="Scan barang ke keranjang" continuous @detected="handleCode" />
</template>
