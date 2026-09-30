<script setup lang="ts">
import { PlusIcon } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { Badge } from '@/components/ui/badge'
import type { Product } from '@/types'
import { formatRupiah } from '@/utils/format'
import { mediaUrl } from '@/utils/media'

const props = defineProps<{ product: Product; inCart: number }>()
const emit = defineEmits<{ add: [Product] }>()

// gambar gagal dimuat (URL mati / foto dihapus) → kembali ke inisial produk
const imageBroken = ref(false)
const imageSrc = computed(() => (imageBroken.value ? null : mediaUrl(props.product.imageUrl)))
watch(
  () => props.product.imageUrl,
  () => (imageBroken.value = false),
)

const soldOut = computed(() => props.product.stock <= 0)
const maxed = computed(() => props.inCart >= props.product.stock)
const initials = computed(() =>
  props.product.name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase(),
)
const stockVariant = computed(() =>
  props.product.stockStatus === 'OUT' ? 'danger' : props.product.stockStatus === 'LOW' ? 'warning' : 'success',
)

function add() {
  if (!soldOut.value && !maxed.value) emit('add', props.product)
}
</script>

<!-- Kartu dibuat dari <button> (bukan <Card>) supaya bisa diklik & difokus keyboard; gayanya mengikuti Card shadcn. -->
<template>
  <button
    type="button"
    data-slot="card"
    class="group flex flex-col overflow-hidden rounded-xl border bg-card text-left text-card-foreground shadow-sm transition duration-200 outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
    :class="
      soldOut ? 'cursor-not-allowed opacity-55' : 'hover:-translate-y-0.5 hover:border-ring/50 hover:shadow-md active:translate-y-0'
    "
    :disabled="soldOut"
    :aria-label="`Tambah ${product.name}`"
    @click="add"
  >
    <div class="relative flex h-28 items-center justify-center bg-muted">
      <img v-if="imageSrc" :src="imageSrc" :alt="product.name" class="h-full w-full object-cover" loading="lazy" @error="imageBroken = true" />
      <span v-else class="text-3xl font-extrabold tracking-tight text-muted-foreground/40 select-none">{{ initials }}</span>

      <Badge :variant="stockVariant" class="absolute top-2.5 right-2.5 shadow-sm">
        {{ soldOut ? 'Habis' : `Stok ${product.stock}` }}
      </Badge>
      <Badge v-if="inCart > 0" class="absolute top-2.5 left-2.5 min-w-6 font-bold shadow-sm">{{ inCart }}</Badge>
    </div>

    <div class="flex flex-1 flex-col gap-1 p-3.5">
      <div class="flex items-center justify-between gap-2">
        <span class="truncate font-mono text-[11px] text-muted-foreground">{{ product.sku }}</span>
        <span v-if="product.categoryName" class="truncate text-[11px] font-medium text-muted-foreground">
          {{ product.categoryName }}
        </span>
      </div>
      <h3 class="line-clamp-2 min-h-[2.6rem] text-sm leading-snug font-semibold">{{ product.name }}</h3>
      <div class="mt-auto flex items-end justify-between gap-2 pt-1.5">
        <div>
          <p class="num text-base font-bold">{{ formatRupiah(product.sellingPrice) }}</p>
          <p class="text-[11px] text-muted-foreground">per {{ product.unit }}</p>
        </div>
        <span
          class="flex size-8 items-center justify-center rounded-md transition"
          :class="soldOut || maxed ? 'bg-muted text-muted-foreground' : 'bg-primary text-primary-foreground group-hover:bg-primary/90'"
        >
          <PlusIcon class="size-[17px]" />
        </span>
      </div>
    </div>
  </button>
</template>
