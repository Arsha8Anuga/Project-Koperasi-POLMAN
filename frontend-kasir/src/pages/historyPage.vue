<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { salesApi } from '../services/salesApi'
import { formatRupiah } from '../utils/formatRupiah'
import { formatDateTime } from '../utils/formatDateTime'
import type { Transaction } from '../types/transaction'

const router = useRouter()

const rows = ref<Transaction[]>([])
const page = ref(1)
const limit = 10
const totalPages = ref(1)
const loading = ref(false)
const errorMsg = ref('')

async function load() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await salesApi.mine(page.value, limit)
    rows.value = res.data
    totalPages.value = res.meta.totalPages
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Terjadi kesalahan'
  } finally {
    loading.value = false
  }
}

function goTo(p: number) {
  if (p < 1 || p > totalPages.value || loading.value) return
  page.value = p
  load()
}

onMounted(load)
</script>

<template>
  <div class="mx-auto max-w-2xl px-4 py-6">
    <div class="flex items-center gap-3">
      <button
        type="button"
        @click="router.push('/pos')"
        class="rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-600 transition hover:bg-indigo-100"
      >
        ← Kembali ke Kasir
      </button>
      <h2 class="text-lg font-bold text-slate-900">Riwayat Transaksi</h2>
    </div>

    <div class="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <p v-if="loading" class="p-4 text-center text-sm text-slate-500">Memuat...</p>
      <p v-else-if="errorMsg" class="p-4 text-center text-sm font-medium text-rose-500">{{ errorMsg }}</p>
      <p v-else-if="rows.length === 0" class="p-4 text-center text-sm text-slate-400">Belum ada transaksi.</p>

      <table v-else class="w-full text-sm">
        <thead>
          <tr class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-400">
            <th class="px-4 py-2.5">Kode</th>
            <th class="px-4 py-2.5">Waktu</th>
            <th class="px-4 py-2.5">Metode</th>
            <th class="px-4 py-2.5 text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="tx in rows"
            :key="tx.id"
            class="cursor-pointer border-t border-slate-100 transition hover:bg-indigo-50/50"
            @click="router.push(`/invoice/${tx.id}`)"
          >
            <td class="px-4 py-2.5 font-medium text-slate-800">{{ tx.code }}</td>
            <td class="px-4 py-2.5 text-slate-500">{{ formatDateTime(tx.createdAt) }}</td>
            <td class="px-4 py-2.5 text-slate-500">{{ tx.payment.method }}</td>
            <td class="px-4 py-2.5 text-right font-semibold text-slate-800">{{ formatRupiah(tx.total) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="mt-4 flex items-center justify-center gap-4">
      <button
        type="button"
        :disabled="page <= 1 || loading"
        @click="goTo(page - 1)"
        class="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-200 disabled:opacity-40"
      >
        Sebelumnya
      </button>
      <span class="text-xs text-slate-500">Halaman {{ page }} / {{ totalPages }}</span>
      <button
        type="button"
        :disabled="page >= totalPages || loading"
        @click="goTo(page + 1)"
        class="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-200 disabled:opacity-40"
      >
        Berikutnya
      </button>
    </div>
  </div>
</template>