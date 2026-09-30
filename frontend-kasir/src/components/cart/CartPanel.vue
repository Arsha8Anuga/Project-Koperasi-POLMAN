<script setup lang="ts">
import { MinusIcon, PlusIcon, ShoppingBagIcon, Trash2Icon } from '@lucide/vue'
import { useRouter } from 'vue-router'
import CartSuggestions from '@/components/cart/CartSuggestions.vue'
import ProductImage from '@/components/product/ProductImage.vue'
import { Button } from '@/components/ui/button'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
import { useCartStore } from '@/stores/cart'
import { formatRupiah } from '@/utils/format'

/** Panel "Detail pesanan": dipakai di sisi kanan (layar lebar) dan di sheet bawah (HP/tablet). */
const emit = defineEmits<{ checkout: [] }>()
const cart = useCartStore()
const router = useRouter()

function onQtyInput(productId: string, e: Event) {
  const v = Number((e.target as HTMLInputElement).value)
  if (Number.isFinite(v)) cart.setQty(productId, Math.floor(v))
}

function checkout() {
  emit('checkout')
  router.push({ name: 'payment' })
}
</script>

<template>
  <div class="flex h-full flex-col">
    <div class="flex items-center justify-between gap-2 px-5 pt-5 pb-3">
      <div>
        <h2 class="text-lg font-bold tracking-tight">Detail pesanan</h2>
        <p class="text-xs text-muted-foreground">
          {{ cart.isEmpty ? 'Belum ada barang' : `${cart.items.length} produk · ${cart.totalQty} barang` }}
        </p>
      </div>
      <Button v-if="!cart.isEmpty" variant="ghost" size="sm" class="text-muted-foreground hover:text-destructive" @click="cart.clear()">
        Kosongkan
      </Button>
    </div>

    <Empty v-if="cart.isEmpty" class="flex-1">
      <EmptyHeader>
        <EmptyMedia variant="icon"><ShoppingBagIcon /></EmptyMedia>
        <EmptyTitle>Pesanan masih kosong</EmptyTitle>
        <EmptyDescription>Klik produk atau scan barcode untuk menambahkannya.</EmptyDescription>
      </EmptyHeader>
    </Empty>

    <ul v-else class="flex-1 space-y-2.5 overflow-y-auto px-4 pb-3">
      <li v-for="item in cart.items" :key="item.productId" class="flex gap-3 rounded-2xl border bg-background/60 p-2.5">
        <ProductImage :src="item.imageUrl" :name="item.name" class="size-[4.5rem] shrink-0 rounded-xl" text-class="text-lg" />
        <div class="flex min-w-0 flex-1 flex-col">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold">{{ item.name }}</p>
              <p class="num truncate text-xs text-muted-foreground">{{ formatRupiah(item.price) }} / {{ item.unit }}</p>
            </div>
            <Button
              variant="ghost"
              size="icon-xs"
              class="-mt-0.5 -mr-0.5 text-muted-foreground hover:text-destructive"
              :aria-label="`Hapus ${item.name}`"
              @click="cart.remove(item.productId)"
            >
              <Trash2Icon />
            </Button>
          </div>
          <div class="mt-auto flex items-center justify-between gap-2 pt-1.5">
            <div class="flex items-center gap-1.5">
              <Button
                size="icon-xs"
                class="size-7 rounded-full"
                :aria-label="`Kurangi ${item.name}`"
                @click="cart.setQty(item.productId, item.quantity - 1)"
              >
                <MinusIcon />
              </Button>
              <input
                :value="item.quantity"
                type="number"
                min="1"
                :max="item.stock"
                class="num h-7 w-10 rounded-md bg-transparent text-center text-sm font-bold outline-none [appearance:textfield] focus-visible:bg-accent [&::-webkit-inner-spin-button]:appearance-none"
                :aria-label="`Jumlah ${item.name}`"
                @change="onQtyInput(item.productId, $event)"
              />
              <Button
                size="icon-xs"
                class="size-7 rounded-full"
                :aria-label="`Tambah ${item.name}`"
                :disabled="item.quantity >= item.stock"
                @click="cart.setQty(item.productId, item.quantity + 1)"
              >
                <PlusIcon />
              </Button>
            </div>
            <p class="num text-sm font-bold">{{ formatRupiah(item.price * item.quantity) }}</p>
          </div>
          <p v-if="item.quantity >= item.stock" class="mt-1 text-[11px] font-medium text-warning">
            Maksimal sesuai stok ({{ item.stock }})
          </p>
        </div>
      </li>
    </ul>

    <CartSuggestions />

    <div class="space-y-3 p-4">
      <dl class="space-y-1.5 rounded-2xl border bg-background/60 px-4 py-3 text-sm">
        <div class="flex justify-between text-muted-foreground">
          <dt>Jumlah barang</dt>
          <dd class="num font-medium text-foreground">{{ cart.totalQty }}</dd>
        </div>
        <div class="flex justify-between text-muted-foreground">
          <dt>Subtotal</dt>
          <dd class="num font-medium text-foreground">{{ formatRupiah(cart.totalAmount) }}</dd>
        </div>
        <div class="mt-2 flex items-baseline justify-between border-t border-dashed pt-2.5">
          <dt class="font-semibold">Total bayar</dt>
          <dd class="num text-xl font-extrabold tracking-tight">{{ formatRupiah(cart.totalAmount) }}</dd>
        </div>
      </dl>
      <Button size="lg" class="h-12 w-full rounded-xl text-[15px]" :disabled="cart.isEmpty" @click="checkout">
        Lanjut ke pembayaran
      </Button>
    </div>
  </div>
</template>
