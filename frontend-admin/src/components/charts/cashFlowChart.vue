<script setup lang="ts">
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement,
  CategoryScale, LinearScale, Filler,
} from 'chart.js'
import { reportsApi } from '../../services/reportsApi'
import { formatRupiah } from '../../utils/formatRupiah'
import type { CashflowItem, ReportParams } from '../../types/report'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

const items = ref<CashflowItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

async function load(params: ReportParams) {
  loading.value = true
  errorMsg.value = ''
  try {
    items.value = await reportsApi.cashflow(params)
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
      label: 'Pemasukan',
      data: items.value.map((i) => i.income),
      borderColor: '#22c55e',
      backgroundColor: 'rgba(34,197,94,0.1)',
      tension: 0.4,
      pointRadius: 0,
      fill: true,
    },
    {
      label: 'Pengeluaran',
      data: items.value.map((i) => i.expense),
      borderColor: '#ef4444',
      backgroundColor: 'rgba(239,68,68,0.1)',
      tension: 0.4,
      pointRadius: 0,
      fill: true,
    },
    {
      label: 'Net',
      data: items.value.map((i) => i.net),
      borderColor: '#334155',
      backgroundColor: 'transparent',
      tension: 0.4,
      pointRadius: 0,
      fill: false,
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
        label: (ctx: any) => `${ctx.dataset.label}: ${formatRupiah(ctx.raw)}`,
      },
    },
  },
  scales: {
    y: { beginAtZero: true },
  },
}
</script>

<template>
  <div class="card">
    <h3>Arus Kas</h3>

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