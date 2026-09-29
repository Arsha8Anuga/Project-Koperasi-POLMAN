<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import InvoiceView from '../components/invoice/InvoiceView.vue'
import { usePdf } from '../composables/usePdf'
import { salesApi } from '../services/salesApi'
import type { Transaction } from '../types/transaction'

const route = useRoute()
const router = useRouter()

const transaction = ref<Transaction | null>(null)
const loading = ref(true)
const loadError = ref('')

const invoiceEl = ref<HTMLElement | null>(null)
const downloading = ref(false)
const errorMsg = ref('')
const { download } = usePdf()

onMounted(async () => {
  try {
    transaction.value = await salesApi.getById(route.params.id as string)
  } catch (e) {
    loadError.value = e instanceof Error ? e.message : 'Transaksi tidak ditemukan'
  } finally {
    loading.value = false
  }
})

async function downloadPdf() {
  if (!invoiceEl.value || downloading.value || !transaction.value) return
  downloading.value = true
  errorMsg.value = ''
  try {
    await download(invoiceEl.value, `${transaction.value.code}.pdf`)
  } catch {
    errorMsg.value = 'Gagal membuat PDF. Coba lagi.'
  } finally {
    downloading.value = false
  }
}

function printInvoice() {
  window.print()
}
</script>

<template>
  <div class="mx-auto max-w-md px-4 py-6 text-center">
    <p v-if="loading" class="text-sm text-slate-500">Memuat invoice...</p>
    <p v-else-if="loadError" class="text-sm font-medium text-rose-500">{{ loadError }}</p>

    <template v-else-if="transaction">
      <div ref="invoiceEl" class="print-area">
        <InvoiceView :transaction="transaction" />
      </div>

      <div class="mt-4 flex flex-wrap justify-center gap-2">
        <button
          type="button"
          :disabled="downloading"
          @click="downloadPdf"
          class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-700 disabled:bg-slate-300"
        >
          {{ downloading ? 'Membuat PDF...' : 'Unduh PDF' }}
        </button>
        <button
          type="button"
          @click="printInvoice"
          class="rounded-xl bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-200"
        >
          Cetak
        </button>
        <button
          type="button"
          @click="router.push('/history')"
          class="rounded-xl bg-indigo-50 px-4 py-2 text-sm font-semibold text-indigo-600 transition hover:bg-indigo-100"
        >
          Kembali ke Riwayat
        </button>
      </div>

      <p v-if="errorMsg" class="mt-2 text-sm font-medium text-rose-500">{{ errorMsg }}</p>
    </template>
  </div>
</template>

<style>
@media print {
  body * { visibility: hidden; }
  .print-area, .print-area * { visibility: visible; }
  .print-area { position: absolute; left: 0; top: 0; }
}
</style>