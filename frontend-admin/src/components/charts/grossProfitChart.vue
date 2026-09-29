<script setup lang="ts">
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement,
  CategoryScale, LinearScale, Filler,
} from 'chart.js'
import { reportsApi } from '../../services/reportsApi'
import { formatRupiah } from '../../utils/formatRupiah'
import type { GrossProfitItem, ReportParams } from '../../types/report'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

const items = ref<GrossProfitItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

async function load(params: ReportParams) {
  loading.value = true
  errorMsg.value = ''
  try {
    items.value = await reportsApi.grossProfit(params)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Terjadi kesalahan'
  } finally {
    loading.value = false
  }
}
defineExpose({ load })

const chartData = computed(() => ({
  labels: items.value.map((i) => i.period),
  datasets: [
    {
      label: 'Laba Kotor',
      data: items.value.map((i) => i.grossProfit),
      borderColor: '#3b82f6',
      backgroundColor: 'rgba(59,130,246,0.1)',
      tension: 0.4,
      pointRadius: 0,
      fill: true,
      yAxisID: 'y',
    },
    {
      label: 'Margin (%)',
      data: items.value.map((i) => i.margin),
      borderColor: '#f59e0b',
      backgroundColor: 'transparent',
      tension: 0.4,
      pointRadius: 0,
      fill: false,
      yAxisID: 'y1',
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index' as const, intersect: false },
  plugins: {
    tooltip: {
      callbacks: {
        label: (ctx: any) =>
          ctx.dataset.label === 'Laba Kotor'
            ? `Laba Kotor: ${formatRupiah(ctx.raw)}`
            : `Margin: ${ctx.raw}%`,
      },
    },
  },
  scales: {
    y: {
      type: 'linear' as const,
      position: 'left' as const,
      beginAtZero: true,
      title: { display: true, text: 'Rupiah' },
    },
    y1: {
      type: 'linear' as const,
      position: 'right' as const,
      beginAtZero: true,
      grid: { drawOnChartArea: false },
      title: { display: true, text: 'Margin (%)' },
    },
  },
}
</script>

<template>
  <div class="card">
    <h3>Laba Kotor</h3>

    <p v-if="loading">Memuat...</p>
    <p v-else-if="errorMsg" class="warn">{{ errorMsg }}</p>
    <p v-else-if="items.length === 0">Belum ada data.</p>

    <div v-else style="height: 340px">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.card { max-width: 640px; margin: 0 auto; padding: 16px; border: 1px solid #ccc; }
h3 { margin-top: 0; text-align: center; }
.warn { color: #c00; text-align: center; }
</style>