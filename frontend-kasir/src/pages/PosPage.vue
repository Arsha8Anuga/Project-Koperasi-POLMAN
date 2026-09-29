<script setup lang="ts">
import { CircleAlertIcon, RefreshCwIcon, SearchIcon, SearchXIcon, XIcon } from '@lucide/vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import CartPanel from '@/components/cart/CartPanel.vue'
import ProductCard from '@/components/product/ProductCard.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Input } from '@/components/ui/input'
import { Kbd } from '@/components/ui/kbd'
import { Skeleton } from '@/components/ui/skeleton'
import { errorMessage } from '@/services/api'
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
async function loadProducts() {
  const id = ++requestId
  loading.value = true
  error.value = ''
  try {
    const res = await catalogApi.products({ search: search.value.trim(), categoryId: categoryId.value })
    if (id !== requestId) return // respons lama datang belakangan: abaikan
    products.value = res.data
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
            class="h-11 pr-12 pl-11 text-[15px] md:text-[15px]"
            placeholder="Cari nama produk, SKU, atau scan barcode…"
            aria-label="Cari produk"
          />
          <Button
            v-if="search"
            variant="ghost"
            size="icon-sm"
            class="absolute top-1/2 right-1.5 -translate-y-1/2"
            aria-label="Hapus pencarian"
            @click="search = ''"
          >
            <XIcon />
          </Button>
          <Kbd v-else class="absolute top-1/2 right-3 hidden -translate-y-1/2 sm:inline-flex">/</Kbd>
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
</template>
