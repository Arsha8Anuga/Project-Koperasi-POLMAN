<script setup lang="ts">
import { Badge } from '@/components/ui/badge'
import type { StockStatus } from '@/types/api'

defineProps<{ status: StockStatus }>()
const label: Record<StockStatus, string> = { OK: 'Aman', LOW: 'Menipis', OUT: 'Habis' }
const variant = { OK: 'success', LOW: 'warning', OUT: 'danger' } as const
</script>

<template>
  <Badge :variant="variant[status]">{{ label[status] }}</Badge>
</template>
