<script setup lang="ts">
import { PackageIcon } from '@lucide/vue'
import { ref, watch } from 'vue'
import { cn } from '@/lib/utils'
import { mediaUrl } from '@/utils/media'

/** Gambar produk kecil. Tanpa gambar, atau gambar gagal dimuat → ikon placeholder. */
const props = defineProps<{ src: string | null | undefined; alt?: string; class?: string }>()
const broken = ref(false)
watch(
  () => props.src,
  () => (broken.value = false),
)
</script>

<template>
  <span :class="cn('flex size-10 shrink-0 items-center justify-center overflow-hidden rounded-md border bg-muted', props.class)">
    <img
      v-if="src && !broken"
      :src="mediaUrl(src) ?? undefined"
      :alt="alt ?? ''"
      class="h-full w-full object-cover"
      loading="lazy"
      @error="broken = true"
    />
    <PackageIcon v-else class="size-[45%] text-muted-foreground/60" aria-hidden="true" />
  </span>
</template>
