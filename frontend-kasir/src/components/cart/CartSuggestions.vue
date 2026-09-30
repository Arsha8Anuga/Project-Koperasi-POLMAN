<script setup lang="ts">
import { PlusIcon, SparklesIcon } from '@lucide/vue'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import ProductImage from '@/components/product/ProductImage.vue'
import { Button } from '@/components/ui/button'
import { insightApi } from '@/services/insightApi'
import { useCartStore } from '@/stores/cart'
import type { Suggestion } from '@/types'
import { formatRupiah } from '@/utils/format'

/**
 * "Sering dibeli bersama" — hasil association rules dari AI engine.
 * Kalau engine belum menghitung / error, komponen ini diam saja (tidak mengganggu kasir).
 */
const cart = useCartStore()
const items = ref<Suggestion[]>([])

const key = computed(() => cart.items.map((i) => i.productId).sort().join(','))

let timer: ReturnType<typeof setTimeout> | undefined
let requestId = 0
watch(
  key,
  (ids) => {
    clearTimeout(timer)
    if (!ids) {
      items.value = []
      return
    }
    timer = setTimeout(async () => {
      const id = ++requestId
      try {
        const result = await insightApi.frequentlyBought(ids.split(','))
        if (id === requestId) items.value = result
      } catch {
        if (id === requestId) items.value = []
      }
    }, 300)
  },
  { immediate: true },
)
onBeforeUnmount(() => clearTimeout(timer))

const percent = (v: number) => `${Math.round(v * 100)}%`
</script>

<template>
  <div v-if="items.length" class="mx-4 rounded-2xl bg-accent/50 px-3 py-3">
    <p class="mb-2 flex items-center gap-1.5 text-xs font-semibold tracking-wide text-accent-foreground uppercase">
      <SparklesIcon class="size-3.5" /> Sering dibeli bersama
    </p>
    <ul class="space-y-1.5">
      <li v-for="s in items" :key="s.product.id" class="flex items-center gap-2.5 rounded-xl bg-card p-1.5 pr-2 shadow-xs">
        <ProductImage :src="s.product.imageUrl" :name="s.product.name" class="size-10 shrink-0 rounded-lg" text-class="text-xs" />
        <div class="min-w-0 flex-1 leading-tight">
          <p class="truncate text-sm font-medium">{{ s.product.name }}</p>
          <p class="truncate text-[11px] text-muted-foreground">
            {{ percent(s.confidence) }} pembeli {{ s.because.join(' + ') }} juga membeli ini
          </p>
        </div>
        <span class="num text-xs font-semibold">{{ formatRupiah(s.product.sellingPrice) }}</span>
        <Button size="icon-sm" variant="secondary" :aria-label="`Tambah ${s.product.name}`" @click="cart.add(s.product)">
          <PlusIcon />
        </Button>
      </li>
    </ul>
  </div>
</template>
