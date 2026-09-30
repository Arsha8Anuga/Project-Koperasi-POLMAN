<script setup lang="ts">
import { MinusIcon, PlusIcon, ShoppingCartIcon, TrashIcon } from '@lucide/vue'
import { useRouter } from 'vue-router'
import CartSuggestions from '@/components/cart/CartSuggestions.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { Separator } from '@/components/ui/separator'
import { useCartStore } from '@/stores/cart'
import { formatRupiah } from '@/utils/format'

const cart = useCartStore()
const router = useRouter()

function onQtyInput(productId: string, e: Event) {
  const v = Number((e.target as HTMLInputElement).value)
  if (Number.isFinite(v)) cart.setQty(productId, Math.floor(v))
}
</script>

<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center justify-between px-5 py-4">
      <div class="flex items-center gap-2.5">
        <ShoppingCartIcon class="size-[19px] text-muted-foreground" />
        <h2 class="text-base font-semibold">Keranjang</h2>
        <Badge v-if="!cart.isEmpty" variant="soft">{{ cart.totalQty }} item</Badge>
      </div>
      <Button v-if="!cart.isEmpty" variant="ghost" size="sm" class="hover:text-destructive" @click="cart.clear()">
        Kosongkan
      </Button>
    </div>
    <Separator />

    <Empty v-if="cart.isEmpty" class="flex-1">
      <EmptyHeader>
        <EmptyMedia variant="icon"><ShoppingCartIcon /></EmptyMedia>
        <EmptyTitle>Keranjang masih kosong</EmptyTitle>
        <EmptyDescription>Klik produk di sebelah kiri untuk menambahkannya.</EmptyDescription>
      </EmptyHeader>
    </Empty>

    <ul v-else class="flex-1 space-y-2 overflow-y-auto px-3 py-3">
      <li v-for="item in cart.items" :key="item.productId" class="rounded-lg border bg-muted/50 p-3">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold">{{ item.name }}</p>
            <p class="num text-xs text-muted-foreground">{{ formatRupiah(item.price) }} / {{ item.unit }}</p>
          </div>
          <Button
            variant="ghost"
            size="icon-xs"
            class="text-muted-foreground hover:text-destructive"
            :aria-label="`Hapus ${item.name}`"
            @click="cart.remove(item.productId)"
          >
            <TrashIcon />
          </Button>
        </div>
        <div class="mt-2.5 flex items-center justify-between">
          <div class="flex items-center overflow-hidden rounded-md border bg-background shadow-xs">
            <Button
              variant="ghost"
              size="icon-sm"
              class="rounded-none"
              aria-label="Kurangi"
              @click="cart.setQty(item.productId, item.quantity - 1)"
            >
              <MinusIcon />
            </Button>
            <input
              :value="item.quantity"
              type="number"
              min="1"
              :max="item.stock"
              class="num h-8 w-12 border-x bg-transparent text-center text-sm font-semibold outline-none [appearance:textfield] focus-visible:bg-accent [&::-webkit-inner-spin-button]:appearance-none"
              :aria-label="`Jumlah ${item.name}`"
              @change="onQtyInput(item.productId, $event)"
            />
            <Button
              variant="ghost"
              size="icon-sm"
              class="rounded-none"
              aria-label="Tambah"
              :disabled="item.quantity >= item.stock"
              @click="cart.setQty(item.productId, item.quantity + 1)"
            >
              <PlusIcon />
            </Button>
          </div>
          <p class="num text-sm font-bold">{{ formatRupiah(item.price * item.quantity) }}</p>
        </div>
        <p v-if="item.quantity >= item.stock" class="mt-1.5 text-[11px] font-medium text-warning">
          Maksimal sesuai stok ({{ item.stock }})
        </p>
      </li>
    </ul>

    <CartSuggestions />

    <div class="border-t bg-card px-5 py-4">
      <div class="mb-1 flex justify-between text-sm text-muted-foreground">
        <span>Jumlah barang</span>
        <span class="num font-semibold text-foreground">{{ cart.totalQty }}</span>
      </div>
      <div class="mb-4 flex items-baseline justify-between">
        <span class="text-sm font-semibold text-muted-foreground">Total</span>
        <span class="num text-2xl font-extrabold tracking-tight">{{ formatRupiah(cart.totalAmount) }}</span>
      </div>
      <Button size="lg" class="h-11 w-full text-[15px]" :disabled="cart.isEmpty" @click="router.push({ name: 'payment' })">
        Lanjut ke Pembayaran
      </Button>
    </div>
  </div>
</template>
