<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import './setup'
import { useChartTheme } from '@/composables/useChartTheme'
import type { StockReportItem } from '@/types/api'

/** Stok vs stok minimum. Batang merah/kuning = perlu restock. */
const props = defineProps<{ items: StockReportItem[] }>()
const t = useChartTheme()

const data = computed<ChartData<'bar'>>(() => ({
  labels: props.items.map((i) => i.sku),
  datasets: [
    {
      label: 'Stok',
      data: props.items.map((i) => i.stock),
      backgroundColor: props.items.map((i) =>
        i.stockStatus === 'OUT' ? t.value.danger : i.stockStatus === 'LOW' ? t.value.warning : t.value.navy,
      ),
      borderRadius: 4,
      maxBarThickness: 26,
    },
    {
      label: 'Stok minimum',
      data: props.items.map((i) => i.minimumStock),
      backgroundColor: t.value.dark ? 'rgba(154,167,191,0.25)' : 'rgba(83,96,122,0.18)',
      borderRadius: 4,
      maxBarThickness: 26,
    },
  ],
}))

const options = computed<ChartOptions<'bar'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { position: 'bottom', labels: { color: t.value.text } },
    tooltip: { callbacks: { title: (items) => props.items[items[0]?.dataIndex ?? 0]?.name ?? '' } },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: t.value.text, maxRotation: 60, autoSkip: false, font: { size: 10 } } },
    y: { beginAtZero: true, grid: { color: t.value.grid }, border: { display: false }, ticks: { color: t.value.text, precision: 0 } },
  },
}))
</script>

<template>
  <Bar :data="data" :options="options" />
</template>
