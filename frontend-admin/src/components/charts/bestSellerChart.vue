<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import './setup'
import { useChartTheme } from '@/composables/useChartTheme'
import type { BestSellerReport } from '@/types/api'
import { formatNumber, formatRupiah } from '@/utils/format'

const props = defineProps<{ report: BestSellerReport }>()
const t = useChartTheme()

const data = computed<ChartData<'bar'>>(() => ({
  labels: props.report.items.map((i) => (i.name.length > 24 ? `${i.name.slice(0, 23)}…` : i.name)),
  datasets: [
    {
      label: 'Terjual',
      data: props.report.items.map((i) => i.quantitySold),
      backgroundColor: props.report.items.map((_, idx) => (idx < 3 ? t.value.navy : t.value.steel)),
      borderRadius: 4,
      maxBarThickness: 22,
    },
  ],
}))

const options = computed<ChartOptions<'bar'>>(() => ({
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        title: (items) => props.report.items[items[0]?.dataIndex ?? 0]?.name ?? '',
        label: (ctx) => {
          const item = props.report.items[ctx.dataIndex]
          if (!item) return ''
          return `${formatNumber(item.quantitySold)} terjual · ${formatRupiah(item.revenue)}`
        },
      },
    },
  },
  scales: {
    x: { beginAtZero: true, grid: { color: t.value.grid }, border: { display: false }, ticks: { color: t.value.text, precision: 0 } },
    y: { grid: { display: false }, ticks: { color: t.value.fg, font: { weight: 600 } } },
  },
}))
</script>

<template>
  <Bar :data="data" :options="options" />
</template>
