<script setup lang="ts">
import { BRAND } from '@/utils/brand'

/** Logo toko. Gambar diambil dari public/logo.svg — ganti file itu untuk memasang logo asli. */
withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })
</script>

<template>
  <img
    :src="BRAND.logo"
    :alt="`Logo ${BRAND.name}`"
    class="shrink-0 rounded-xl bg-muted object-contain ring-1 ring-border"
    :class="{
      'size-8': size === 'sm',
      'size-10': size === 'md',
      'size-14 rounded-2xl': size === 'lg',
    }"
    draggable="false"
  />
</template>
