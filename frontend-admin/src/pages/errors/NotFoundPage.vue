<script setup lang="ts">
import { MapPinOffIcon } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
</script>

<template>
  <Empty class="min-h-screen">
    <EmptyHeader>
      <EmptyMedia variant="icon" class="size-16 [&_svg:not([class*='size-'])]:size-8"><MapPinOffIcon /></EmptyMedia>
      <p class="num text-5xl font-extrabold tracking-tight">404</p>
      <EmptyTitle class="text-xl font-bold">Halaman tidak ditemukan</EmptyTitle>
      <EmptyDescription>Alamat yang Anda buka tidak ada atau sudah dipindahkan.</EmptyDescription>
    </EmptyHeader>
    <EmptyContent>
      <Button as-child><RouterLink to="/">Kembali ke dashboard</RouterLink></Button>
    </EmptyContent>
  </Empty>
</template>
