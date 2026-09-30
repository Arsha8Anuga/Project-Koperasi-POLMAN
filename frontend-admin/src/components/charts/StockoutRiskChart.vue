<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import './setup'
import { useChartTheme } from '@/composables/useChartTheme'
import type { ForecastSummary } from '@/types/api'
import { formatDays, urgency } from '@/utils/insight'

/** "Stok habis dalam … hari" untuk produk paling mendesak. Merah = sudah di bawah lead time supplier. */
const props = withDefaults(
  defineProps<{ items: ForecastSummary[]; limit?: number; leadTime?: number; reviewDays?: number }>(),
  { limit: 12, leadTime: 3, reviewDays: 7 },
)
const emit = defineEmits<{ select: [productId: string] }>()
const t = useChartTheme()

const CAP = 30 // batang dipotong di 30 hari supaya produk yang aman tidak mendominasi
const rows = computed(() => props.items.filter((p) => p.daysUntilStockout !== null).slice(0, props.limit))

const data = computed<ChartData<'bar'>>(() => ({
  labels: rows.value.map((p) => (p.name.length > 22 ? `${p.name.slice(0, 21)}…` : p.name)),
  datasets: [
    {
      label: 'Hari sampai stok habis',
      data: rows.value.map((p) => Math.min(p.daysUntilStockout ?? CAP, CAP)),
      backgroundColor: rows.value.map((p) => {
        const u = urgency(p.daysUntilStockout, props.leadTime, props.reviewDays)
        return u === 'danger' ? t.value.danger : u === 'warning' ? t.value.warning : t.value.navy
      }),
      borderRadius: 4,
      maxBarThickness: 20,
    },
  ],
}))

const options = computed<ChartOptions<'bar'>>(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  onClick: (_e, elements) => {
    const i = elements[0]?.index
    const p = i === undefined ? undefined : rows.value[i]
    if (p) emit('select', p.productId)
  },
  onHover: (e, elements) => {
    const target = e.native?.target as HTMLElement | undefined
    if (target) target.style.cursor = elements.length ? 'pointer' : 'default'
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (items) => rows.value[items[0]?.dataIndex ?? 0]?.name ?? '',
        label: (ctx) => {
          const p = rows.value[ctx.dataIndex]
          if (!p) return ''
          return [
            `Habis dalam ${formatDays(p.daysUntilStockout)} (stok ${p.stock}, ±${p.avgDaily}/hari)`,
            p.suggestedQty > 0 ? `Saran restock: ${p.suggestedQty} ${p.unit}` : 'Belum perlu restock',
          ]
        },
      },
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      max: CAP,
      title: { display: true, text: 'Hari (dipotong di 30)', color: t.value.text },
      grid: { color: t.value.grid },
      border: { display: false },
      ticks: { color: t.value.text },
    },
    y: { grid: { display: false }, ticks: { color: t.value.fg, font: { weight: 600 } } },
  },
}))
</script>

<template>
  <Bar :data="data" :options="options" />
</template>
