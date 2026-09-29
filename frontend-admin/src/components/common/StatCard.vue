<script setup lang="ts">
import type { Component } from 'vue'
import { Card, CardContent } from '@/components/ui/card'

withDefaults(
  defineProps<{
    label: string
    value: string
    hint?: string
    icon?: Component
    tone?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral'
  }>(),
  { tone: 'primary' },
)

const toneClass = {
  primary: 'bg-secondary text-secondary-foreground',
  success: 'bg-success-soft text-success',
  warning: 'bg-warning-soft text-warning',
  danger: 'bg-destructive/10 text-destructive',
  neutral: 'bg-muted text-muted-foreground',
}
</script>

<template>
  <Card class="py-5">
    <CardContent class="flex items-start gap-4 px-5">
      <span v-if="icon" class="flex size-11 shrink-0 items-center justify-center rounded-lg" :class="toneClass[tone]">
        <component :is="icon" class="size-[21px]" />
      </span>
      <div class="min-w-0">
        <p class="text-[13px] font-semibold text-muted-foreground">{{ label }}</p>
        <p class="num mt-0.5 truncate text-2xl font-extrabold tracking-tight">{{ value }}</p>
        <p v-if="hint" class="mt-0.5 text-xs text-muted-foreground">{{ hint }}</p>
      </div>
    </CardContent>
  </Card>
</template>
