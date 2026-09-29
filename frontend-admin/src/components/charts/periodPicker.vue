<script setup lang="ts">
import { ref } from 'vue'
import type { Granularity, ReportParams } from '../../types/report'

const emit = defineEmits<{ (e: 'change', params: ReportParams): void }>()

const options: { label: string; value: Granularity }[] = [
  { label: 'Harian', value: 'HARIAN' },
  { label: 'Mingguan', value: 'MINGGUAN' },
  { label: 'Bulanan', value: 'BULANAN' },
  { label: 'Tahunan', value: 'TAHUNAN' },
]

const active = ref<Granularity>('HARIAN')

function toISO(d: Date) {
  return d.toISOString().slice(0, 10)
}

function rangeFor(g: Granularity) {
  const now = new Date()
  const start = new Date(now)
  if (g === 'HARIAN') start.setDate(now.getDate() - 30)
  else if (g === 'MINGGUAN') start.setDate(now.getDate() - 12 * 7)
  else if (g === 'BULANAN') start.setMonth(now.getMonth() - 12)
  else start.setFullYear(now.getFullYear() - 5)
  return { from: toISO(start), to: toISO(now) }
}

function select(g: Granularity) {
  active.value = g
  const { from, to } = rangeFor(g)
  emit('change', { granularity: g, from, to })
}

select(active.value)
</script>

<template>
  <div class="tabs">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      class="tab"
      :class="{ active: active === opt.value }"
      @click="select(opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  background: #f1f5f9;
  border-radius: 999px;
  margin-bottom: 16px;
}
.tab {
  border: none;
  background: transparent;
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
}
.tab:hover { color: #334155; }
.tab.active {
  background: #ffffff;
  color: #0f172a;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
</style>