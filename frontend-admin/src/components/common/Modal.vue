<script setup lang="ts">
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'

/**
 * Dialog form standar (shadcn Dialog). `open` dikontrol parent; tutup (Esc, klik luar, tombol X) → emit `close`.
 */
const props = withDefaults(defineProps<{ open: boolean; title: string; description?: string; size?: 'sm' | 'md' | 'lg' }>(), {
  size: 'md',
})
const emit = defineEmits<{ close: [] }>()

function onOpenChange(v: boolean) {
  if (!v) emit('close')
}
const width = { sm: 'sm:max-w-sm', md: 'sm:max-w-lg', lg: 'sm:max-w-3xl' }
</script>

<template>
  <Dialog :open="props.open" @update:open="onOpenChange">
    <DialogContent :class="['max-h-[90vh] overflow-y-auto', width[size]]">
      <DialogHeader>
        <DialogTitle class="text-lg font-bold">{{ title }}</DialogTitle>
        <DialogDescription :class="!description && 'sr-only'">{{ description ?? title }}</DialogDescription>
      </DialogHeader>
      <slot />
    </DialogContent>
  </Dialog>
</template>
