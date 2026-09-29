<script setup lang="ts">
defineProps<{
  open: boolean
  title?: string
  message?: string
  confirmText?: string
  danger?: boolean
}>()
const emit = defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-sm rounded-xl bg-white p-6 shadow-lg">
      <h2 class="text-lg font-semibold">{{ title ?? 'Konfirmasi' }}</h2>
      <p class="mt-2 text-sm text-gray-600">{{ message ?? 'Apakah kamu yakin?' }}</p>
      <div class="mt-6 flex justify-end gap-3">
        <button class="rounded-lg border px-4 py-2 text-sm hover:bg-gray-50" @click="emit('cancel')">
          Batal
        </button>
        <button
          class="rounded-lg px-4 py-2 text-sm font-medium text-white"
          :class="danger ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-600 hover:bg-blue-700'"
          @click="emit('confirm')"
        >
          {{ confirmText ?? 'Ya, lanjutkan' }}
        </button>
      </div>
    </div>
  </div>
</template>