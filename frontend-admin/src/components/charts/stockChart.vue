<script setup lang="ts">
import { ref, computed } from 'vue'
import { Chart as ChartComponent } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineElement, PointElement,
  CategoryScale, LinearScale, BarController, LineController,
} from 'chart.js'
import { reportsApi } from '../../services/reportsApi'
import type { StockItem, StockStatus, ReportParams } from '../../types/report'

ChartJS.register(
  Title, Tooltip, Legend, BarElement, LineElement, PointElement,
  CategoryScale, LinearScale, BarController, LineController,
)

const items = ref<StockItem[]>([])
const loading = ref(false)
const errorMsg = ref('')

const statusColor: Record<StockStatus, string> = {
  AMAN: '#22c55e',
  MENIPIS: '#f59e0b',
  HABIS: '#ef4444',
}

async function load(params: ReportParams) {
  loading.value = true
  errorMsg.value = ''
  try {
    items.value = await reportsApi.stock(params)
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
      type: 'bar' as const,
      label: 'Stok',
      data: items.value.map((i) => i.stock),
      backgroundColor: items.value.map((i) => statusColor[i.stockStatus]),
    },
    {
      type: 'line' as const,
      label: 'Stok minimum',
      data: items.value.map((i) => i.minimumStock),
      borderColor: '#334155',
      borderDash: [6, 4],
      pointRadius: 0,
      fill: false,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: { y: { beginAtZero: true } },
}
</script>

<template>
  <div class="card">
    <h3>Stok Produk</h3>

    <p v-if="loading">Memuat...</p>
    <p v-else-if="errorMsg" class="warn">{{ errorMsg }}</p>
    <p v-else-if="items.length === 0">Belum ada data.</p>

    <div v-else style="height: 320px">
      <ChartComponent type="bar" :data="chartData" :options="chartOptions" />
    </div>

    <div v-if="items.length" class="legend">
      <span><i :style="{ background: statusColor.AMAN }" /> Aman</span>
      <span><i :style="{ background: statusColor.MENIPIS }" /> Menipis</span>
      <span><i :style="{ background: statusColor.HABIS }" /> Habis</span>
    </div>
  </div>
</template>

<style scoped>
.card { max-width: 600px; margin: 0 auto; padding: 16px; border: 1px solid #ccc; }
h3 { margin-top: 0; text-align: center; }
.warn { color: #c00; text-align: center; }
.legend { display: flex; gap: 16px; justify-content: center; margin-top: 8px; font-size: 14px; }
.legend i { display: inline-block; width: 10px; height: 10px; margin-right: 4px; border-radius: 2px; }
</style>