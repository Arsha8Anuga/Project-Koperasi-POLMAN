<script setup lang="ts">
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale,
} from 'chart.js'
import { reportsApi } from '../../services/reportsApi'
import { formatRupiah } from '../../utils/formatRupiah'
import type { BestSellerItem, ReportParams } from '../../types/report'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const items = ref<BestSellerItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

async function load(params: ReportParams) {
  loading.value = true
  errorMsg.value = ''
  try {
    items.value = await reportsApi.bestSellers(params)
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : 'Terjadi kesalahan'
  } finally {
    loading.value = false
  }
}
defineExpose({ load })

const chartData = computed(() => ({
  labels: items.value.map((i) => i.name),
  datasets: [
    {
      label: 'Qty terjual',
      data: items.value.map((i) => i.qty),
      backgroundColor: '#3b82f6',
    },
  ],
}))

const chartOptions = computed(() => ({
  indexAxis: 'y' as const,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        afterLabel: (ctx: any) => `Pendapatan: ${formatRupiah(items.value[ctx.dataIndex].revenue)}`,
      },
    },
  },
  scales: {
    x: { beginAtZero: true },
    y: { ticks: { autoSkip: false } },
  },
}))

const chartHeight = computed(() => Math.max(items.value.length * 36, 200))
</script>

<template>
  <div class="card">
    <h3>Best Seller (Top 10)</h3>

    <p v-if="loading">Memuat...</p>
    <p v-else-if="errorMsg" class="warn">{{ errorMsg }}</p>
    <p v-else-if="items.length === 0">Belum ada data.</p>

    <div v-else :style="{ height: chartHeight + 'px' }">
        <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.card { max-width: 600px; margin: 0 auto; padding: 16px; border: 1px solid #ccc; }
h3 { margin-top: 0; text-align: center; }
.warn { color: #c00; text-align: center; }
</style>