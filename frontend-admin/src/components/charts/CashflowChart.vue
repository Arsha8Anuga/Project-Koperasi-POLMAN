<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import { useChartTheme } from '@/composables/useChartTheme'
import type { CashflowReport } from '@/types/api'
import { formatRupiah } from '@/utils/format'
import { compactRupiah, periodLabel } from './setup'

const props = defineProps<{ report: CashflowReport }>()
const t = useChartTheme()

const data = computed<ChartData<'bar'>>(() => ({
  labels: props.report.buckets.map((b) => periodLabel(b.period, props.report.granularity)),
  datasets: [
    {
      label: 'Pemasukan (penjualan)',
      data: props.report.buckets.map((b) => b.income),
      backgroundColor: t.value.navy,
      borderRadius: 4,
      maxBarThickness: 28,
    },
    {
      label: 'Pengeluaran (restock)',
      data: props.report.buckets.map((b) => b.expense),
      backgroundColor: t.value.steel,
      borderRadius: 4,
      maxBarThickness: 28,
    },
  ],
}))

const options = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', labels: { color: t.value.text } },
    tooltip: {
      callbacks: {
        label: (ctx) => `${ctx.dataset.label}: ${formatRupiah(ctx.parsed.y ?? 0)}`,
        footer: (items) => {
          const b = props.report.buckets[items[0]?.dataIndex ?? 0]
          return b ? `Arus kas bersih: ${formatRupiah(b.net)}` : ''
        },
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: t.value.text, maxRotation: 0, autoSkipPadding: 12 } },
    y: {
      beginAtZero: true,
      grid: { color: t.value.grid },
      border: { display: false },
      ticks: { color: t.value.text, callback: (v) => compactRupiah(v) },
    },
  },
}))
</script>

<template>
  <Bar :data="data" :options="options" />
</template>
