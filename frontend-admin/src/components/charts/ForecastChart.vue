<script setup lang="ts">
import type { ChartData, ChartOptions } from 'chart.js'
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import './setup'
import { useChartTheme } from '@/composables/useChartTheme'
import type { ForecastDetail } from '@/types/api'
import { formatNumber } from '@/utils/format'

/**
 * Penjualan aktual (garis penuh) → prediksi 14 hari (putus-putus) dengan rentang ±80% (area),
 * plus perkiraan sisa stok (sumbu kanan) supaya titik "stok habis" terlihat.
 */
const props = defineProps<{ detail: ForecastDetail }>()
const t = useChartTheme()

const label = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', weekday: 'short' })

const data = computed<ChartData<'line'>>(() => {
  const h = props.detail.history
  const f = props.detail.forecast
  const pad = (n: number) => Array<number | null>(n).fill(null)
  const lastActual = h.length ? h[h.length - 1]!.qty : null

  let stock = props.detail.stock
  const remaining = f.map((p) => {
    stock = Math.max(0, stock - p.qty)
    return Math.round(stock * 10) / 10
  })

  return {
    labels: [...h.map((p) => label(p.date)), ...f.map((p) => label(p.date))],
    datasets: [
      {
        label: 'Terjual (aktual)',
        data: [...h.map((p) => p.qty), ...pad(f.length)],
        borderColor: t.value.navy,
        backgroundColor: t.value.navy,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        tension: 0.25,
      },
      {
        label: 'Prediksi',
        // disambung dari titik aktual terakhir supaya garis tidak putus
        data: [...pad(Math.max(0, h.length - 1)), lastActual, ...f.map((p) => p.qty)],
        borderColor: t.value.accent,
        backgroundColor: t.value.accent,
        borderDash: [6, 4],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        tension: 0.25,
      },
      {
        label: 'Rentang atas',
        data: [...pad(h.length), ...f.map((p) => p.upper ?? p.qty)],
        borderWidth: 0,
        pointRadius: 0,
        backgroundColor: t.value.dark ? 'rgba(59,111,216,0.22)' : 'rgba(59,111,216,0.14)',
        fill: '+1',
      },
      {
        label: 'Rentang bawah',
        data: [...pad(h.length), ...f.map((p) => p.lower ?? p.qty)],
        borderWidth: 0,
        pointRadius: 0,
      },
      {
        label: 'Perkiraan sisa stok',
        data: [...pad(h.length), ...remaining],
        borderColor: t.value.warning,
        backgroundColor: t.value.warning,
        borderWidth: 1.5,
        borderDash: [2, 3],
        pointRadius: 0,
        yAxisID: 'stock',
      },
    ],
  }
})

const options = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'bottom',
      labels: { color: t.value.text, filter: (item) => !String(item.text).startsWith('Rentang') },
    },
    tooltip: {
      filter: (item) => item.raw !== null && !String(item.dataset.label).startsWith('Rentang'),
      callbacks: {
        label: (ctx) => `${ctx.dataset.label}: ${formatNumber(Math.round((ctx.parsed.y ?? 0) * 10) / 10)}`,
        afterBody: (items) => {
          const i = (items[0]?.dataIndex ?? 0) - props.detail.history.length
          const p = i >= 0 ? props.detail.forecast[i] : undefined
          return p && p.lower != null && p.upper != null
            ? `Rentang 80%: ${formatNumber(Math.round(p.lower))}–${formatNumber(Math.round(p.upper))}`
            : ''
        },
      },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { color: t.value.text, maxRotation: 0, autoSkipPadding: 14 } },
    y: {
      beginAtZero: true,
      title: { display: true, text: `Unit per hari (${props.detail.unit})`, color: t.value.text },
      grid: { color: t.value.grid },
      border: { display: false },
      ticks: { color: t.value.text, precision: 0 },
    },
    stock: {
      position: 'right',
      beginAtZero: true,
      title: { display: true, text: 'Sisa stok', color: t.value.text },
      grid: { display: false },
      border: { display: false },
      ticks: { color: t.value.text, precision: 0 },
    },
  },
}))
</script>

<template>
  <Line :data="data" :options="options" />
</template>
