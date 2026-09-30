<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { cn } from '@/lib/utils'
import { mediaUrl } from '@/utils/media'

/** Foto produk; tanpa foto atau gagal dimuat → inisial nama produk (fallback seperti sebelumnya). */
const props = defineProps<{ src?: string | null; name: string; class?: string; textClass?: string }>()

const broken = ref(false)
watch(
  () => props.src,
  () => (broken.value = false),
)
const url = computed(() => (broken.value ? null : mediaUrl(props.src)))
const initials = computed(() =>
  props.name
    .split(' ')
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase(),
)
</script>

<template>
  <div :class="cn('relative flex items-center justify-center overflow-hidden bg-muted', props.class)">
    <img v-if="url" :src="url" :alt="name" class="h-full w-full object-cover" loading="lazy" @error="broken = true" />
    <span
      v-else
      :class="cn('font-extrabold tracking-tight text-muted-foreground/45 select-none', props.textClass ?? 'text-2xl')"
      aria-hidden="true"
      >{{ initials }}</span
    >
    <slot />
  </div>
</template>
