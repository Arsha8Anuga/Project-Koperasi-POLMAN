<script setup lang="ts">
import { ref, computed } from 'vue'
import { formatRupiah } from '../../utils/formatRupiah'

const props = defineProps<{
  total: number
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'submit', amountPaid: number): void
}>()

const amountPaid = ref<number>(0)

const change = computed(() => Math.max(amountPaid.value - props.total, 0))
const isEnough = computed(() => amountPaid.value >= props.total)

const quickAmounts = [20000, 50000, 100000]

function setExact() {
  amountPaid.value = props.total
}

function submit() {
  if (!isEnough.value || props.loading) return
  emit('submit', amountPaid.value)
}
</script>

<template>
  <div class="max-w-sm mx-auto rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
    <p class="text-sm text-slate-500">
      Total: <span class="font-bold text-slate-900">{{ formatRupiah(total) }}</span>
    </p>

    <label class="mt-4 block text-xs font-semibold uppercase tracking-wide text-slate-400">
      Uang diterima
      <input
        v-model.number="amountPaid"
        type="number"
        min="0"
        class="mt-1 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-800 outline-none transition focus:border-indigo-400 focus:bg-white focus:ring-4 focus:ring-indigo-100"
      />
    </label>
    <p class="mt-1 text-xs text-slate-400">{{ formatRupiah(amountPaid || 0) }}</p>

    <div class="mt-3 flex flex-wrap gap-2">
      <button
        type="button"
        @click="setExact"
        class="rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-600 transition hover:bg-indigo-100"
      >
        Uang Pas
      </button>
      <button
        v-for="n in quickAmounts"
        :key="n"
        type="button"
        @click="amountPaid = n"
        class="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-200"
      >
        {{ n.toLocaleString('id-ID') }}
      </button>
    </div>

    <div class="mt-4 flex items-center justify-between text-sm">
      <span class="text-slate-500">Kembalian</span>
      <span class="text-base font-bold text-slate-900">{{ formatRupiah(change) }}</span>
    </div>
    <p v-if="!isEnough" class="mt-1 text-xs font-medium text-rose-500">
      Uang kurang {{ formatRupiah(total - (amountPaid || 0)) }}
    </p>

    <button
      type="button"
      :disabled="!isEnough || loading"
      @click="submit"
      class="mt-4 w-full rounded-xl bg-indigo-600 py-3 text-sm font-bold text-white shadow-md transition hover:bg-indigo-700 disabled:bg-slate-300 disabled:shadow-none"
    >
      {{ loading ? 'Memproses...' : 'Selesaikan' }}
    </button>
  </div>
</template>