<script setup lang="ts">
import { SearchIcon } from '@lucide/vue'
import { Input } from '@/components/ui/input'

withDefaults(defineProps<{ placeholder?: string }>(), { placeholder: 'Cari…' })
const model = defineModel<string>({ required: true })
</script>

<template>
  <div class="relative min-w-56 flex-1">
    <SearchIcon class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
    <Input v-model="model" class="pl-9" :placeholder="placeholder" :aria-label="placeholder" />
  </div>
</template>
