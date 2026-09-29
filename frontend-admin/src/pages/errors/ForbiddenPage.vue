<script setup lang="ts">
import { ShieldAlertIcon } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '@/components/ui/empty'
</script>

<template>
  <Empty class="min-h-screen">
    <EmptyHeader>
      <EmptyMedia variant="icon" class="size-16 bg-destructive/10 text-destructive [&_svg:not([class*='size-'])]:size-8">
        <ShieldAlertIcon />
      </EmptyMedia>
      <p class="num text-5xl font-extrabold tracking-tight">403</p>
      <EmptyTitle class="text-xl font-bold">Akses ditolak</EmptyTitle>
      <EmptyDescription>Akun Anda tidak memiliki izin untuk membuka halaman ini.</EmptyDescription>
    </EmptyHeader>
    <EmptyContent>
      <Button as-child><RouterLink :to="{ name: 'dashboard' }">Kembali ke dashboard</RouterLink></Button>
    </EmptyContent>
  </Empty>
</template>
