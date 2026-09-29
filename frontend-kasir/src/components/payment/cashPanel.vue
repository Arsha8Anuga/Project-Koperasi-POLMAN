<script setup lang="ts">
import { computed, ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Field, FieldLabel } from '@/components/ui/field'
import { Spinner } from '@/components/ui/spinner'
import { cn } from '@/lib/utils'
import { formatNumber, formatRupiah } from '@/utils/format'

const props = defineProps<{ total: number; loading?: boolean }>()
const emit = defineEmits<{ submit: [amountPaid: number] }>()

const amount = ref<number | null>(null)
const paid = computed(() => amount.value ?? 0)
const enough = computed(() => paid.value >= props.total && props.total > 0)
const change = computed(() => Math.max(paid.value - props.total, 0))
const short = computed(() => amount.value !== null && !enough.value)

/** Uang pas + pembulatan ke atas yang umum dipakai pembeli. */
const quickAmounts = computed(() => {
  const set = new Set<number>()
  for (const step of [5_000, 10_000, 50_000, 100_000]) {
    const v = Math.ceil(props.total / step) * step
    if (v > props.total) set.add(v)
  }
  return [...set].sort((a, b) => a - b).slice(0, 4)
})

function onInput(e: Event) {
  const digits = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  amount.value = digits ? Math.min(Number(digits), 1_000_000_000) : null
}

function submit() {
  if (enough.value && !props.loading) emit('submit', paid.value)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="submit">
    <Field>
      <FieldLabel for="amount-paid">Uang diterima</FieldLabel>
      <div class="relative">
        <span class="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 text-lg font-semibold text-muted-foreground">Rp</span>
        <!-- input polos (bukan komponen Input) karena nilainya diformat ribuan saat diketik -->
        <input
          id="amount-paid"
          :value="amount === null ? '' : formatNumber(amount)"
          inputmode="numeric"
          autocomplete="off"
          placeholder="0"
          :aria-invalid="short || undefined"
          :class="
            cn(
              'num h-14 w-full rounded-md border border-input bg-transparent pr-4 pl-12 text-2xl font-bold shadow-xs outline-none transition-[color,box-shadow] dark:bg-input/30',
              'focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50',
              'aria-invalid:border-destructive aria-invalid:ring-destructive/20',
            )
          "
          autofocus
          @input="onInput"
        />
      </div>
    </Field>

    <div class="grid grid-cols-2 gap-2 sm:grid-cols-5">
      <Button type="button" variant="secondary" size="sm" @click="amount = total">Uang pas</Button>
      <Button v-for="v in quickAmounts" :key="v" type="button" variant="outline" size="sm" class="num" @click="amount = v">
        {{ formatNumber(v) }}
      </Button>
    </div>

    <div
      class="flex items-center justify-between rounded-lg border px-4 py-3"
      :class="short ? 'border-destructive/30 bg-destructive/8' : 'bg-muted/50'"
    >
      <span class="text-sm font-semibold" :class="short ? 'text-destructive' : 'text-muted-foreground'">
        {{ short ? 'Uang kurang' : 'Kembalian' }}
      </span>
      <span class="num text-xl font-extrabold" :class="short ? 'text-destructive' : 'text-success'">
        {{ formatRupiah(short ? total - paid : change) }}
      </span>
    </div>

    <Button type="submit" size="lg" class="h-12 w-full text-[15px]" :disabled="!enough || loading">
      <Spinner v-if="loading" />
      {{ loading ? 'Memproses…' : 'Selesaikan Pembayaran' }}
    </Button>
  </form>
</template>
