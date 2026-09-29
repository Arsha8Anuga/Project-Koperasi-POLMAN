<script setup lang="ts">
import { ref, watch } from 'vue'
import { toDataURL } from 'qrcode'
import { formatRupiah } from '../../utils/formatRupiah'

const props = defineProps<{
  total: number
  loading?: boolean // true saat request berjalan
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
}>()

const qrImage = ref<string>('')
const errorMsg = ref<string>('')

// Buat ulang QR setiap kali total berubah (dan sekali saat komponen muncul)
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
  <div class="panel">
    <p>Total: <strong>{{ formatRupiah(total) }}</strong></p>

    <img v-if="qrImage" :src="qrImage" alt="QR pembayaran QRIS" width="240" height="240" />
    <p v-if="errorMsg" class="warn">{{ errorMsg }}</p>

    <p class="muted">Minta pelanggan memindai QR, lalu tekan tombol setelah pembayaran masuk.</p>

    <button type="button" :disabled="!qrImage || loading" @click="confirm">
      {{ loading ? 'Memproses...' : 'Pembayaran Diterima' }}
    </button>
  </div>
</template>

<style scoped>
.panel { max-width: 320px; margin: 16px auto; padding: 16px; border: 1px solid #ccc; text-align: center; }
.muted { color: #666; font-size: 14px; }
.warn { color: #c00; }
</style>