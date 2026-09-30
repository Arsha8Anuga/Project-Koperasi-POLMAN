<script setup lang="ts">
import { ArrowLeftIcon, CircleAlertIcon, CircleCheckIcon, DownloadIcon, PrinterIcon, ShoppingCartIcon } from '@lucide/vue'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from 'vue-sonner'
import InvoiceView from '@/components/invoice/InvoiceView.vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Spinner } from '@/components/ui/spinner'
import { usePdf } from '@/composables/usePdf'
import { errorMessage } from '@/services/api'
import { salesApi } from '@/services/salesApi'
import type { Sale } from '@/types'
import { formatRupiah } from '@/utils/format'

const route = useRoute()
const { download } = usePdf()

const sale = ref<Sale | null>(null)
const loading = ref(true)
const error = ref('')
const receipt = ref<HTMLElement | null>(null)
const downloading = ref(false)
const isNew = route.query.new === '1'

onMounted(async () => {
  try {
    sale.value = await salesApi.get(String(route.params.id))
  } catch (e) {
    error.value = errorMessage(e, 'Transaksi tidak ditemukan')
  } finally {
    loading.value = false
  }
})

function printReceipt() {
  window.print()
}

async function downloadPdf() {
  if (!receipt.value || !sale.value || downloading.value) return
  downloading.value = true
  try {
    await download(receipt.value, `${sale.value.code}.pdf`)
  } catch {
    toast.error('Gagal membuat PDF', { description: 'Gunakan tombol Cetak lalu pilih "Simpan sebagai PDF".' })
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="mx-auto max-w-xl px-4 py-6 sm:px-6">
      <div class="no-print mb-5 flex items-center gap-3">
        <Button as-child variant="ghost" size="icon" aria-label="Kembali">
          <RouterLink :to="{ name: 'history' }"><ArrowLeftIcon class="size-5" /></RouterLink>
        </Button>
        <h1 class="text-2xl font-bold">Struk</h1>
      </div>

      <Skeleton v-if="loading" class="mx-auto h-[28rem] w-[300px] rounded-xl" />

      <Alert v-else-if="error" variant="destructive">
        <CircleAlertIcon />
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>

      <template v-else-if="sale">
        <Alert v-if="isNew" variant="success" class="no-print mb-5">
          <CircleCheckIcon />
          <AlertTitle>Transaksi berhasil — {{ sale.code }}</AlertTitle>
          <AlertDescription v-if="sale.payment.method === 'CASH'" class="num">
            <p>Kembalian: <strong>{{ formatRupiah(sale.payment.change) }}</strong></p>
          </AlertDescription>
        </Alert>

        <div class="rounded-xl bg-muted p-5 sm:p-8">
          <div ref="receipt" class="print-area">
            <InvoiceView :sale="sale" />
          </div>
        </div>

        <div class="no-print mt-5 grid grid-cols-3 gap-2">
          <Button variant="outline" :disabled="downloading" @click="downloadPdf">
            <Spinner v-if="downloading" />
            <DownloadIcon v-else /> PDF
          </Button>
          <Button variant="outline" @click="printReceipt"><PrinterIcon /> Cetak</Button>
          <Button as-child>
            <RouterLink :to="{ name: 'pos' }"><ShoppingCartIcon /> Transaksi baru</RouterLink>
          </Button>
        </div>
      </template>
    </div>
  </div>
</template>
<style>
@media print {
  body * {
    visibility: hidden;
  }
  .print-area,
  .print-area * {
    visibility: visible;
  }
  .print-area {
    position: absolute;
    top: 0;
    left: 0;
  }
  .receipt {
    box-shadow: none !important;
  }
}
</style>
