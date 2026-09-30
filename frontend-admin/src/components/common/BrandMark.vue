<script setup lang="ts">
import { BRAND } from '@/utils/brand'

/**
 * Logo toko (public/logo.svg — ganti file itu untuk memasang logo asli). ISI FILE INI IDENTIK di kedua app.
 * `plain`: tanpa kotak latar & bingkai (mis. di halaman login). Latar yang ADA DI DALAM file gambar
 * tetap terlihat — pakai PNG/SVG transparan kalau ingin benar-benar tanpa latar.
 */
withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' | 'xl'; plain?: boolean }>(), { size: 'md', plain: false })
</script>

<template>
  <img
    :src="BRAND.logo"
    :alt="`Logo ${BRAND.name}`"
    class="shrink-0 object-contain"
    :class="[
      plain ? '' : 'rounded-xl bg-muted ring-1 ring-border',
      {
        'size-8': size === 'sm',
        'size-10': size === 'md',
        'size-14': size === 'lg',
        'size-24 sm:size-28': size === 'xl',
        'rounded-2xl': size === 'lg' && !plain,
      },
    ]"
    draggable="false"
  />
</template>
