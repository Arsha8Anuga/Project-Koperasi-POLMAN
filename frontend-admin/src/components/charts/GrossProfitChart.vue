<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import { useChartTheme } from '@/composables/useChartTheme'
import type { GrossProfitReport } from '@/types/api'
import { formatRupiah } from '@/utils/format'
import { compactRupiah, periodLabel } from './setup'

const props = defineProps<{ report: GrossProfitReport }>()
const t = useChartTheme()

const data = computed<ChartData<'line'>>(() => ({
  labels: props.report.buckets.map((b) => periodLabel(b.period, props.report.granularity)),
  datasets: [
    {
      label: 'Pendapatan',
      data: props.report.buckets.map((b) => b.revenue),
      borderColor: t.value.steel,
      backgroundColor: 'transparent',
      borderWidth: 2,
      borderDash: [5, 4],
      pointRadius: 0,
      tension: 0.35,
    },
    {
      label: 'Laba kotor',
      data: props.report.buckets.map((b) => b.grossProfit),
      borderColor: t.value.accent,
      backgroundColor: t.value.dark ? 'rgba(59,111,216,0.22)' : 'rgba(59,111,216,0.12)',
      borderWidth: 2.5,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.35,
      fill: true,
    },
  ],
}))

const options = computed<ChartOptions<'line'>>(() => ({
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
          return b ? `HPP: ${formatRupiah(b.cogs)} · Margin ${(b.margin * 100).toFixed(1)}%` : ''
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
  <Line :data="data" :options="options" />
</template>
