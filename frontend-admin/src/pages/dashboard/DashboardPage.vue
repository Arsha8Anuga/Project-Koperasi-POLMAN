<script setup lang="ts">
import { onMounted, ref } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import { dashboardApi } from '@/services/dashboardApi'
import { useAuthStore } from '@/stores/auth'
import type { DashboardSummary } from '@/types/api'
import { formatRupiah } from '@/utils/format'

const auth = useAuthStore()
const summary = ref<DashboardSummary>({})
const loading = ref(true)

onMounted(async () => {
  if (!auth.user) return
  try {
    summary.value = await dashboardApi.summary(auth.user.role)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-4">
    <h1 class="text-lg font-semibold">Dashboard</h1>
    <p v-if="loading" class="text-sm text-gray-400">Memuat data...</p>

    <div v-else class="grid grid-cols-3 gap-4">
      <template v-if="auth.user?.role === 'OWNER'">
        <StatCard label="Penjualan Hari Ini" :value="formatRupiah(summary.todaySales ?? 0)" accent="green" />
        <StatCard label="Jumlah Transaksi Hari Ini" :value="String(summary.todayTransactionCount ?? 0)" accent="blue" />
        <StatCard label="Laba Kotor Bulan Ini" :value="formatRupiah(summary.grossProfitThisMonth ?? 0)" accent="green" />
      </template>

      <template v-else-if="auth.user?.role === 'LOGISTIK'">
        <StatCard label="Stok Menipis" :value="String(summary.lowStockCount ?? 0)" accent="yellow" />
        <StatCard label="Stok Habis" :value="String(summary.outOfStockCount ?? 0)" accent="red" />
        <StatCard label="Restock Tertunda" :value="String(summary.pendingRestockCount ?? 0)" accent="blue" />
      </template>

      <template v-else-if="auth.user?.role === 'ADMIN'">
        <StatCard label="Total User" :value="String(summary.totalUsers ?? 0)" accent="blue" />
        <StatCard label="Total Anggota" :value="String(summary.totalMembers ?? 0)" accent="blue" />
        <StatCard label="Aktivitas Hari Ini" :value="String(summary.todayAuditCount ?? 0)" accent="blue" />
      </template>
    </div>
  </div>
</template>