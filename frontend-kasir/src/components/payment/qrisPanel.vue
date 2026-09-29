<script setup lang="ts">
import { ref, watch } from 'vue'
import { toDataURL } from 'qrcode'
import { formatRupiah } from '../../utils/formatRupiah'

const props = defineProps<{
  total: number
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
}>()

const qrImage = ref<string>('')
const errorMsg = ref<string>('')

watch(
  () => props.total,
  async (total) => {
    errorMsg.value = ''
    try {
      const payload = `KOPERASI|${total}|${Date.now()}`
      qrImage.value = await toDataURL(payload, { width: 240, margin: 1 })
    } catch {
      qrImage.value = ''
      errorMsg.value = 'Gagal membuat QR. Coba lagi.'
    }
  },
  { immediate: true },
)

function confirm() {
  if (props.loading) return
  emit('confirm')
}
</script>

<template>
  <div class="max-w-sm mx-auto rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-sm">
    <p class="text-sm text-slate-500">
      Total: <span class="font-bold text-slate-900">{{ formatRupiah(total) }}</span>
    </p>

    <img v-if="qrImage" :src="qrImage" alt="QR pembayaran QRIS" width="220" height="220" class="mx-auto mt-4 rounded-xl border border-slate-100 p-2" />
    <p v-if="errorMsg" class="mt-2 text-xs font-medium text-rose-500">{{ errorMsg }}</p>

    <p class="mt-3 text-xs text-slate-400">
      Minta pelanggan memindai QR, lalu tekan tombol setelah pembayaran masuk.
    </p>

    <button
      type="button"
      :disabled="!qrImage || loading"
      @click="confirm"
      class="mt-4 w-full rounded-xl bg-indigo-600 py-3 text-sm font-bold text-white shadow-md transition hover:bg-indigo-700 disabled:bg-slate-300 disabled:shadow-none"
    >
      {{ loading ? 'Memproses...' : 'Pembayaran Diterima' }}
    </button>
  </div>
</template>