<script setup lang="ts">
import { toDataURL } from 'qrcode'
import { ref, watch } from 'vue'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'
import { formatRupiah } from '@/utils/format'

const props = defineProps<{ total: number; loading?: boolean }>()
const emit = defineEmits<{ confirm: [] }>()

const qr = ref('')
const failed = ref(false)

// SIMULASI: QR berisi total belanja, bukan QRIS sungguhan (tidak ada payment gateway di MVP).
watch(
  () => props.total,
  async (total) => {
    failed.value = false
    try {
      qr.value = await toDataURL(`KOPERASI-QRIS|${total}|${Date.now()}`, {
        width: 440,
        margin: 1,
        color: { dark: '#0f1b33', light: '#ffffff' },
      })
    } catch {
      qr.value = ''
      failed.value = true
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="space-y-4 text-center">
    <!-- QR selalu di atas putih supaya bisa dipindai di mode gelap -->
    <div class="mx-auto w-fit rounded-xl border bg-white p-3 shadow-sm">
      <img v-if="qr" :src="qr" alt="Kode QR pembayaran" width="220" height="220" class="block" />
      <p v-else-if="failed" class="flex size-[220px] items-center justify-center text-sm text-slate-500">Gagal membuat QR</p>
      <Skeleton v-else class="size-[220px] bg-slate-200" />
    </div>
    <div>
      <p class="num text-2xl font-extrabold">{{ formatRupiah(total) }}</p>
      <p class="mt-1 text-sm text-muted-foreground">Minta pelanggan memindai QR, lalu konfirmasi setelah pembayaran masuk.</p>
    </div>
    <Button size="lg" class="h-12 w-full text-[15px]" :disabled="!qr || loading" @click="emit('confirm')">
      <Spinner v-if="loading" />
      {{ loading ? 'Memproses…' : 'Pembayaran Diterima' }}
    </Button>
  </div>
</template>
