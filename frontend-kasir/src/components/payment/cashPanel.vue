<script setup lang="ts">
import { ref, computed } from 'vue'
import { formatRupiah } from '../../utils/formatRupiah'

const props = defineProps<{
  total: number
  loading?: boolean // true saat request berjalan, supaya tombol tidak bisa diklik dua kali
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
  <div class="panel">
    <p>Total: <strong>{{ formatRupiah(total) }}</strong></p>

    <label>
      Uang diterima
      <input v-model.number="amountPaid" type="number" min="0" />
    </label>
    <p class="muted">{{ formatRupiah(amountPaid || 0) }}</p>

    <div class="quick">
      <button type="button" @click="setExact">Uang Pas</button>
      <button v-for="n in quickAmounts" :key="n" type="button" @click="amountPaid = n">
        {{ n.toLocaleString('id-ID') }}
      </button>
    </div>

    <p>Kembalian: <strong>{{ formatRupiah(change) }}</strong></p>
    <p v-if="!isEnough" class="warn">Uang kurang {{ formatRupiah(total - (amountPaid || 0)) }}</p>

    <button type="button" :disabled="!isEnough || loading" @click="submit">
      {{ loading ? 'Memproses...' : 'Selesaikan' }}
    </button>
  </div>
</template>

<style scoped>
.panel { max-width: 320px; margin: 16px auto; padding: 16px; border: 1px solid #ccc; }
.quick { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }
.muted { color: #666; margin: 4px 0; }
.warn { color: #c00; }
input { display: block; width: 100%; padding: 6px; margin-top: 4px; }
</style>