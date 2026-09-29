<script setup lang="ts">
import { ChartColumnIcon, CircleAlertIcon } from '@lucide/vue'
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia } from '@/components/ui/empty'
import { Skeleton } from '@/components/ui/skeleton'

defineProps<{ title: string; subtitle?: string; loading?: boolean; error?: string; empty?: boolean; height?: number }>()
</script>

<template>
  <Card class="gap-4">
    <CardHeader>
      <CardTitle class="text-base">{{ title }}</CardTitle>
      <CardDescription v-if="subtitle">{{ subtitle }}</CardDescription>
      <CardAction v-if="$slots.actions"><slot name="actions" /></CardAction>
    </CardHeader>
    <CardContent class="space-y-4">
      <slot name="summary" />
      <div class="relative" :style="{ height: `${height ?? 300}px` }">
        <Skeleton v-if="loading" class="absolute inset-0 rounded-lg" />
        <div
          v-else-if="error"
          class="absolute inset-0 flex flex-col items-center justify-center gap-2 text-center text-sm text-destructive"
        >
          <CircleAlertIcon class="size-[22px]" /> {{ error }}
        </div>
        <Empty v-else-if="empty" class="absolute inset-0 border border-dashed">
          <EmptyHeader>
            <EmptyMedia variant="icon"><ChartColumnIcon /></EmptyMedia>
            <EmptyDescription>Belum ada data pada periode ini</EmptyDescription>
          </EmptyHeader>
        </Empty>
        <slot v-else />
      </div>
    </CardContent>
  </Card>
</template>
