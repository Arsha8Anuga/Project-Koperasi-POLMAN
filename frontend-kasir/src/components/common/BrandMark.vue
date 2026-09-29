<script setup lang="ts">
withDefaults(defineProps<{ size?: 'sm' | 'md' | 'lg' }>(), { size: 'md' })
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center justify-center rounded-xl bg-linear-to-br from-[#2b4f8f] to-[#0f1d3a] font-extrabold tracking-tight text-white shadow-sm ring-1 ring-white/10"
    :class="{
      'h-8 w-8 text-sm': size === 'sm',
      'h-10 w-10 text-base': size === 'md',
      'h-14 w-14 rounded-2xl text-xl': size === 'lg',
    }"
    aria-hidden="true"
  >
    K
  </span>
</template>
