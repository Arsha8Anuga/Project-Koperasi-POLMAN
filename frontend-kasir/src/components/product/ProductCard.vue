<script setup lang="ts">
import { PlusIcon } from '@lucide/vue'
import { computed } from 'vue'
import ProductImage from '@/components/product/ProductImage.vue'
import { Badge } from '@/components/ui/badge'
import type { Product } from '@/types'
import { formatRupiah } from '@/utils/format'

const props = defineProps<{ product: Product; inCart: number }>()
const emit = defineEmits<{ add: [Product] }>()

const soldOut = computed(() => props.product.stock <= 0)
const maxed = computed(() => props.inCart >= props.product.stock)
const stockVariant = computed(() =>
  props.product.stockStatus === 'OUT' ? 'danger' : props.product.stockStatus === 'LOW' ? 'warning' : 'soft',
)

function add() {
  if (!soldOut.value && !maxed.value) emit('add', props.product)
}
</script>

<!--
  Kartu horizontal: info di kiri (kategori/stok, nama, tombol + dan harga di bawah), foto di kanan.
  Seluruh kartu adalah <button> supaya bisa diklik & difokus keyboard.
-->
<template>
  <button
    type="button"
    class="group flex h-40 gap-3 rounded-2xl border bg-card p-3 text-left text-card-foreground shadow-xs transition duration-200 outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 sm:h-44"
    :class="soldOut ? 'cursor-not-allowed opacity-55' : 'hover:border-ring/40 hover:shadow-md'"
    :disabled="soldOut"
    :aria-label="`Tambah ${product.name}`"
    @click="add"
  >
    <div class="flex min-w-0 flex-1 flex-col">
      <div class="flex flex-wrap items-center gap-1.5">
        <Badge v-if="product.categoryName" variant="outline" class="max-w-full truncate rounded-md text-[10.5px] text-muted-foreground">
          {{ product.categoryName }}
        </Badge>
        <Badge :variant="stockVariant" class="rounded-md text-[10.5px]">
          {{ soldOut ? 'Habis' : `Stok ${product.stock}` }}
        </Badge>
      </div>

      <h3 class="mt-2.5 line-clamp-2 text-[15px] leading-snug font-semibold">{{ product.name }}</h3>
      <p class="mt-0.5 truncate font-mono text-[11px] text-muted-foreground">{{ product.sku }} · {{ product.unit }}</p>

      <div class="mt-auto flex items-end justify-between gap-2">
        <span
          class="flex size-9 shrink-0 items-center justify-center rounded-xl transition"
          :class="soldOut || maxed ? 'bg-muted text-muted-foreground' : 'bg-primary text-primary-foreground group-hover:bg-primary/90'"
          aria-hidden="true"
        >
          <PlusIcon class="size-[18px]" />
        </span>
        <p class="num text-right text-base leading-tight font-bold">{{ formatRupiah(product.sellingPrice) }}</p>
      </div>
    </div>

    <ProductImage :src="product.imageUrl" :name="product.name" class="h-full w-[42%] shrink-0 rounded-xl">
      <Badge v-if="inCart > 0" class="absolute top-2 right-2 min-w-6 font-bold shadow-sm">{{ inCart }}</Badge>
    </ProductImage>
  </button>
</template>
