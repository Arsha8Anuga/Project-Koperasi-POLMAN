<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'

/** Konfirmasi aksi (shadcn AlertDialog). Tombol konfirmasi tidak menutup otomatis supaya bisa menampilkan loading. */
const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    message?: string
    confirmText?: string
    danger?: boolean
    loading?: boolean
  }>(),
  { title: 'Konfirmasi', message: 'Lanjutkan tindakan ini?', confirmText: 'Ya, lanjutkan' },
)
const emit = defineEmits<{ confirm: []; cancel: [] }>()

function onOpenChange(v: boolean) {
  if (!v && !props.loading) emit('cancel') // Esc saat proses berjalan diabaikan
}
</script>

<template>
  <AlertDialog :open="open" @update:open="onOpenChange">
    <AlertDialogContent class="sm:max-w-md">
      <AlertDialogHeader>
        <AlertDialogTitle>{{ title }}</AlertDialogTitle>
        <AlertDialogDescription>{{ message }}</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel :disabled="loading">Batal</AlertDialogCancel>
        <Button :variant="danger ? 'destructive' : 'default'" :disabled="loading" @click="emit('confirm')">
          <Spinner v-if="loading" />
          {{ confirmText }}
        </Button>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
