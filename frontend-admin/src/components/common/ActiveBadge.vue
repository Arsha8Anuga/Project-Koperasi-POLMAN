<script setup lang="ts">
import { Badge } from '@/components/ui/badge'

defineProps<{ active: boolean }>()
</script>

<template>
  <Badge :variant="active ? 'success' : 'soft'">
    <span class="size-1.5 rounded-full" :class="active ? 'bg-success' : 'bg-muted-foreground'" />
    {{ active ? 'Aktif' : 'Nonaktif' }}
  </Badge>
</template>
